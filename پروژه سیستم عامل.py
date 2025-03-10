class FreeSpaceManager:
    def __init__(self, total_blocks):
        self.free_blocks = set(range(1, total_blocks))  # Block 0 is reserved

    def allocate_block(self):
        if not self.free_blocks:
            raise Exception("No free blocks available.")
        return self.free_blocks.pop()

    def release_block(self, block):
        if block in self.free_blocks:
            raise Exception(f"Block {block} is already free.")
        self.free_blocks.add(block)

    def get_free_blocks(self):
        return len(self.free_blocks)


class Directory:
    def __init__(self):
        self.structure = {"root": {}}
        self.current_path = ["root"]

    def _get_current_dir(self):
        dir_ref = self.structure
        for dir_name in self.current_path:
            dir_ref = dir_ref[dir_name]
        return dir_ref

    def mkdir(self, directory_name):
        current_dir = self._get_current_dir()
        if directory_name in current_dir:
            print(f"Directory {directory_name} already exists.")
            return
        current_dir[directory_name] = {}

    def rmdir(self, directory_name):
        current_dir = self._get_current_dir()
        if directory_name not in current_dir:
            print(f"Directory {directory_name} does not exist.")
            return
        if current_dir[directory_name]:
            print(f"Directory {directory_name} is not empty.")
            return
        del current_dir[directory_name]

    def ls(self):
        current_dir = self._get_current_dir()
        print(", ".join(current_dir.keys()))

    def cd(self, directory_name):
        if directory_name == "..":
            if len(self.current_path) > 1:
                self.current_path.pop()
            return
        current_dir = self._get_current_dir()
        if directory_name not in current_dir:
            print(f"Directory {directory_name} does not exist.")
            return
        self.current_path.append(directory_name)


class FileSystem:
    def __init__(self, free_space_manager):
        self.free_space_manager = free_space_manager
        self.files = {}

    def create_file(self, filename):
        if filename in self.files:
            print(f"File {filename} already exists.")
            return
        self.files[filename] = {"blocks": [], "size": 0}

    def write_to_file(self, filename, data):
        if filename not in self.files:
            print(f"File {filename} does not exist.")
            return
        required_blocks = (len(data) + BLOCK_SIZE - 1) // BLOCK_SIZE
        if required_blocks > self.free_space_manager.get_free_blocks():
            print("Not enough space to write data.")
            return
        allocated_blocks = []
        for _ in range(required_blocks):
            block = self.free_space_manager.allocate_block()
            allocated_blocks.append(block)
        self.files[filename]["blocks"] = allocated_blocks
        self.files[filename]["size"] = len(data)
        with open(DISK_FILE, "r+b") as disk:
            for i, block in enumerate(allocated_blocks):
                start = block * BLOCK_SIZE
                disk.seek(start)
                disk.write(data[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE].encode())

    def read_file(self, filename):
        if filename not in self.files:
            print(f"File {filename} does not exist.")
            return
        data = ""
        with open(DISK_FILE, "rb") as disk:
            for block in self.files[filename]["blocks"]:
                start = block * BLOCK_SIZE
                disk.seek(start)
                data += disk.read(BLOCK_SIZE).decode().strip("\\x00")
        print(data)

    def delete_file(self, filename):
        if filename not in self.files:
            print(f"File {filename} does not exist.")
            return
        for block in self.files[filename]["blocks"]:
            self.free_space_manager.release_block(block)
        del self.files[filename]


class FileSystemCLI:
    def __init__(self):
        self.free_space_manager = FreeSpaceManager(TOTAL_BLOCKS)
        self.directory_manager = Directory()
        self.file_system = FileSystem(self.free_space_manager)

    def handle_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "touch":
            if len(args) != 1:
                print("Usage: touch <file_name>")
                return
            self.file_system.create_file(args[0])
        elif cmd == "write":
            if len(args) < 2:
                print("Usage: write <file_name> <data>")
                return
            self.file_system.write_to_file(args[0], " ".join(args[1:]))
        elif cmd == "cat":
            if len(args) != 1:
                print("Usage: cat <file_name>")
                return
            self.file_system.read_file(args[0])
        elif cmd == "rm":
            if len(args) != 1:
                print("Usage: rm <file_name>")
                return
            self.file_system.delete_file(args[0])
        elif cmd == "mkdir":
            if len(args) != 1:
                print("Usage: mkdir <directory_name>")
                return
            self.directory_manager.mkdir(args[0])
        elif cmd == "rmdir":
            if len(args) != 1:
                print("Usage: rmdir <directory_name>")
                return
            self.directory_manager.rmdir(args[0])
        elif cmd == "ls":
            self.directory_manager.ls()
        elif cmd == "cd":
            if len(args) != 1:
                print("Usage: cd <directory_name>")
                return
            self.directory_manager.cd(args[0])
        elif cmd == "exit":
            print("Exiting the file system.")
            return "exit"
        else:
            print(f"Unknown command: {cmd}")

    def run(self):
        print("File System Simulator. Type 'exit' to quit.")
        while True:
            command = input(">> ")
            if self.handle_command(command) == "exit":
                break


# Configuration
DISK_FILE = "virtual_disk.bin"
BLOCK_SIZE = 512
TOTAL_BLOCKS = 100

# Initialize the virtual disk
with open(DISK_FILE, "wb") as disk:
    disk.write(bytearray(BLOCK_SIZE * TOTAL_BLOCKS))

if __name__ == "__main__":
    cli = FileSystemCLI()
    cli.run()


# touch testfile
 #write testfile This is a test file.
 #cat testfile

#mkdir testdir
#cd testdir
#touch file_in_dir
# write file_in_dir Directory test content.
#cat file_in_dir
#cd ..
#ls


