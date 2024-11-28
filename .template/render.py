import glob
import logging
import os
import re
import shutil
import sys
import tempfile

from cookiecutter.main import cookiecutter
from git import Repo

logger = logging.getLogger("renderer")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class Renderer:
    """Class to update cookiecutter template from Git remote."""
    
    def __init__(
        self,
        replay_file=".template/cookiecutter.replay.json",
        replay_source="~/.cookiecutter_replay/template.json",
        template_remote="https://github.com/VanOord/template-pyramid-app.git",
    ):
        self.cwd = os.getcwd()
        self.replay_file = os.path.expanduser(replay_file)
        self.replay_source = os.path.expanduser(replay_source)
        self.template_remote = template_remote
        self.template_dir = None
        self.render_dir = None

    def render(self):
        """Render cookiecutter."""
        self._check_cwd()
        logger.info("Starting render...")
        self.merge_template_updates()
        self.create_template_environment()
        self.render_template()
        self.copy_result()
        self.clean_up()
        logger.info("Done.")

    def _check_cwd(self):
        """Check if not in template directory."""
        base = os.path.basename(self.cwd)
        if base == "template-pyramid-app":
            print("I'm in the template repository. Stop.")
            sys.exit()

    def merge_template_updates(self):
        """Merge template updates from Git remote."""
        logger.info("Merge template updates...")
        repo = Repo(self.cwd)
        if "template" not in repo.remotes:
            repo.create_remote("template", self.template_remote)
        repo.git.fetch("template", "master")
        repo.git.merge(
            "template/master", no_commit=True, allow_unrelated_histories=True
        )

    def create_template_environment(self):
        """Create environment to render template."""
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Create template environment in {self.temp_dir}...")
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.template_dir = os.path.join(self.temp_dir, "template")
        self.render_dir = os.path.join(self.temp_dir, "rendered")
        shutil.copytree(".template/", self.template_dir)
        source_dir = os.path.join(self.template_dir, r"{{cookiecutter.project_repo}}")
        shutil.copytree(".", source_dir, ignore=lambda d, f: [".git", ".template"])
        os.makedirs(self.render_dir)

    def render_template(self):
        """Render template."""
        assert self.template_dir is not None
        assert self.render_dir is not None
        logger.info("Rendering template...")
        replay = self.replay_file if os.path.exists(self.replay_file) else None
        cookiecutter(
            self.template_dir,
            overwrite_if_exists=True,
            output_dir=self.render_dir,
            replay=replay,
        )

    def copy_result(self):
        """Copy render result back to Git clone."""
        logger.info("Copying render result...")
        rendered_dir = next(iter(glob.glob(os.path.join(self.render_dir, "*"))))
        shutil.copytree(rendered_dir, ".", dirs_exist_ok=True)
        if not os.path.exists(self.replay_file) and os.path.exists(self.replay_source):
            shutil.copy(self.replay_source, self.replay_file)

    def clean_up(self):
        """Clean up render directory and Git clone."""
        logger.info("Cleaning up...")
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        for root, folders, files in os.walk("."):
            for filename in folders + files:
                if re.search(r"\{\{.+\}\}", filename):
                    shutil.rmtree(os.path.join(root, filename), ignore_errors=True)


if __name__ == "__main__":
    renderer = Renderer()
    renderer.render()
