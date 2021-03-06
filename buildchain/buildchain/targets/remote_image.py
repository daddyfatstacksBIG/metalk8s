# coding: utf-8


"""Provides container image retrieval.

The images are downloaded from a registry.
Then, they are tagged, saved on the disk and optionally compressed.

All of these actions are done by a single task.
"""


import operator
import os
from pathlib import Path
from typing import Any, Optional, List

from buildchain import docker_command
from buildchain import config
from buildchain import types

from . import image


class RemoteImage(image.ContainerImage):
    """A remote container image to download."""

    def __init__(
        self,
        registry: str,
        name: str,
        version: str,
        digest: str,
        destination: Path,
        save_as_tar: bool=False,
        remote_name: Optional[str]=None,
        **kwargs: Any
    ):
        """Initialize a remote container image.

        Arguments:
            registry:       registry where the image is
            name:           image name
            version:        image version
            digest:         image digest
            destination:    save location for the image
            save_as_tar:    save the image as a tar archive?
            remote_name:    image name in the registry

        Keyword Arguments:
            They are passed to `Target` init method.
        """
        self._registry = registry
        self._digest = digest
        self._remote_name = remote_name or name
        self._use_tar = save_as_tar
        kwargs.setdefault('task_dep', []).append('check_for:skopeo')
        super().__init__(
            name=name, version=version,
            destination=destination,
            **kwargs
        )
        self._targets = [self.filepath]

    registry = property(operator.attrgetter('_registry'))
    digest   = property(operator.attrgetter('_digest'))

    @property
    def fullname(self) -> str:
        """Complete image name.

        Usable by `docker` commands.
        """
        return '{obj.registry}/{obj._remote_name}@{obj.digest}'.format(
            obj=self
        )

    @property
    def basicname(self) -> str:
        """Base image name (no digest).

        Usable by `docker` commands.
        """
        return '{obj.registry}/{obj._remote_name}:{obj.version}'.format(
            obj=self
        )


    @property
    def repository(self) -> str:
        """Base image name (no digest).

        Usable by `docker` commands.
        """
        return '{obj.registry}/{obj._remote_name}'.format(
            obj=self
        )


    @property
    def filepath(self) -> Path:
        """Path to the file tracked on disk."""
        if self._use_tar:
            return self.dest_dir/'{obj.name}-{obj.version}{ext}'.format(
                obj=self, ext='.tar'
            )
        # Just to keep track of something on disk.
        return self.dirname/'manifest.json'

    @property
    def task(self) -> types.TaskDict:
        task = self.basic_task
        task.update({
            'title': lambda _: self.show('PULL IMG'),
            'doc': 'Download {} container image.'.format(self.name),
            'uptodate': [True],
        })
        docker_pull = docker_command.DockerPull(
            self.repository,
            self.digest
        )
        docker_tag = docker_command.DockerTag(
                self.repository,
                self.fullname,
                self.version
        )
        docker_save = docker_command.DockerSave(
            self.basicname,
            Path(os.path.join(
                self.dest_dir,
                '{}-{}.tar'.format(self.name, self.version)
            ))
        )
        if self._use_tar:
            task.update({
                'actions': [docker_pull,  docker_tag, docker_save],
            })
        else:
            task.update({
                'actions': [self.mkdirs, self._skopeo_copy()],
                'clean':   [self.clean],
            })
        return task

    def _skopeo_copy(self) -> List[str]:
        """Return the command line to execute skopeo copy."""
        cmd = [
            config.ExtCommand.SKOPEO.value, '--override-os', 'linux',
            '--insecure-policy', 'copy', '--format', 'v2s2'
        ]
        if not self._use_tar:
            cmd.append('--dest-compress')
        cmd.append('docker://{}'.format(self.fullname))
        cmd.append(self._skopeo_dest())
        return cmd

    def _skopeo_dest(self) -> str:
        """Return the destination, formatted for skopeo copy."""
        if self._use_tar:
            return 'docker-archive:{}'.format(self.filepath)
        return 'dir:{}'.format(self.dirname)
