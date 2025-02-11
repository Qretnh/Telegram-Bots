import pytest
from file import File  # Импортируйте ваш класс File из соответствующего модуля
from Directory import Directory


class TestFile:
    def test_init_with_name_only(self):
        file = File(name="example")
        assert file.permissions == "all"
        assert file.root is None

    def test_init_with_name_and_permissions(self):
        file = File(name="example.txt", permissions={'access': 'read', 'view': 'write'})
        assert file.name == "example.txt"
        assert file.extension == "txt"
        assert file.permissions == {'access': 'read', 'view': 'write'}
        assert file.root is None

    def test_init_with_name_and_extension(self):
        file = File(name="example", extension="txt")
        assert file.name == "example"
        assert file.extension == "txt"
        assert file.permissions == "all"
        assert file.root is None

    def test_info(self):
        file = File("example.txt", permissions='all')
        expected_info = (
            'Filename: example.txt\n'
            'Extension: txt\n'
            'Permissions: all'
        )
        assert file.info() == expected_info

    def test_init_with_root(self):
        file = File("example.txt", root="/home/user")
        assert file.root == "/home/user"


class TestDirectory:
    def test_init_with_default_values(self):
        dir = Directory("example_dir")
        assert dir.name == "example_dir"
        assert dir.content == []
        assert dir.permissions == "all"
        assert dir.root is None

    def test_init_with_content(self):
        file = File("file1.txt")
        dir = Directory("example_dir", content=[file])
        assert dir.name == "example_dir"
        assert len(dir.content) == 1
        assert dir.content[0].name == "file1.txt"

    def test_add_file(self):
        dir = Directory("example_dir")
        file = File("file1.txt")
        dir.add(file)
        assert len(dir.content) == 1
        assert dir.content[0].name == "file1.txt"

    def test_get_content_without_param(self):
        dir = Directory("example_dir")
        file1 = File("file1.txt")
        file2 = File("file2.txt")
        dir.add(file1)
        dir.add(file2)
        content = dir.get_content()
        assert len(content) == 2
        assert content[0].name == "file1.txt"
        assert content[1].name == "file2.txt"

    def test_get_content_with_param_dir(self):
        dir = Directory("example_dir")
        subdir = Directory("subdir")
        dir.add(subdir)
        content = dir.get_content(param='dir')
        assert len(content) == 1
        assert content[0].name == "subdir"

    def test_get_content_with_param_file(self):
        dir = Directory("example_dir")
        file = File("file1.txt")
        dir.add(file)
        content = dir.get_content(param='file')
        assert len(content) == 1
        assert content[0].name == "file1.txt"

    def test_filenames_without_param(self):
        dir = Directory("example_dir")
        file = File("file1.txt")
        dir.add(file)
        names = dir.filenames()
        assert len(names) == 1
        assert names[0] == "file1.txt"

    def test_filenames_with_param_dir(self):
        dir = Directory("example_dir")
        subdir = Directory("subdir")
        dir.add(subdir)
        names = dir.filenames(param='dir')
        assert len(names) == 1
        assert names[0] == "subdir"
