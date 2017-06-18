import os
import shutil
from os.path import join

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from portal.models import Node
from portal.models import SharedNode

TEST_ROOT = join(settings.BASE_DIR, '.TESTING_DELETE_ME', )
VALID_DAYS = 7


@override_settings(
    ROOT_DIRECTORY=join(TEST_ROOT, 'source'),
    ROOT_SHARE_PATH=join(TEST_ROOT, 'shared'),
)
class SharedNodeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='admin')
        try:
            os.makedirs(TEST_ROOT)
        except FileExistsError:
            shutil.rmtree(TEST_ROOT)
            os.makedirs(TEST_ROOT)

        movies = join(settings.ROOT_DIRECTORY, 'movies')
        self.movie_dir = join(movies, 'the matrices')
        os.makedirs(self.movie_dir)
        self.movie_file = f"{join(self.movie_dir,'movie_inside_parent.mkv')}"
        open(self.movie_file, 'a')
        open(f"{join(movies,'movie_without_parent.mkv')}", 'a')
        call_command('traverse')
        self.movie_file_node = Node.objects.get(absolute_path=self.movie_file)
        self.movie_dir_node = Node.objects.get(absolute_path=self.movie_dir)

        future = timezone.now() + timezone.timedelta(days=VALID_DAYS)
        self.shared_file = SharedNode.objects.create(expiration=timezone.now(),
                                                     user=self.user,
                                                     node=self.movie_file_node
                                                     )
        self.shared_directory = SharedNode.objects.create(expiration=future,
                                                          user=self.user,
                                                          node=self.movie_dir_node
                                                          )

    def test_create_uuid_directory(self):
        self.assertTrue(os.path.isdir(f'{join(settings.ROOT_SHARE_PATH, str(self.shared_directory))}'))

    def test_create_symlink(self):
        # Check symlink exists inside hash dir
        self.assertTrue(os.path.exists(join(settings.ROOT_SHARE_PATH, str(self.shared_file),
                                            os.path.basename(self.shared_file.node.absolute_path))))

    def test_prune_inactive_shares(self):
        SharedNode.objects.prune_expired()
        with self.assertRaises(SharedNode.DoesNotExist):
            SharedNode.objects.get(pk=self.shared_file.id)

    def test_share_url(self):
        pass

    def test_get_child_url(self):
        self.shared_file.get_child_url(self.movie_file_node)

    def test_remove_dir(self):
        # Hashed dir is removed. Source remains safe.
        self.shared_directory.delete()
        self.assertFalse(os.path.exists(f'{join(settings.ROOT_SHARE_PATH, str(self.shared_directory))}'))
        self.assertTrue(os.path.exists(self.movie_dir))

    def test_remove_file(self):
        self.shared_file.delete()
        self.assertFalse(os.path.exists(f'{join(settings.ROOT_SHARE_PATH, str(self.shared_file))}'))
        self.assertTrue(os.path.exists(self.movie_file))

    def tearDown(self):
        shutil.rmtree(TEST_ROOT)
