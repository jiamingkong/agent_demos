---
name: file_compression
description: File compression and decompression capabilities using Python's standard library (zipfile, tarfile, gzip, bz2).
allowed-tools:
  - compress_file
  - compress_directory
  - decompress_archive
  - list_archive_contents
  - get_archive_info
---

# File Compression Skill

This skill enables the agent to compress and decompress files and directories using various archive formats.

## Supported Formats

- **zip**: Standard ZIP archive (deflated)
- **tar**: Uncompressed tar archive
- **tar.gz**: Gzip-compressed tar archive
- **tar.bz2**: Bzip2-compressed tar archive

## Tools

### compress_file
Compress a single file into an archive.

Args:
- `source_path`: Absolute path to the source file.
- `archive_path`: Absolute path for the output archive (include extension, e.g., `.zip`, `.tar.gz`).
- `format`: Archive format, one of: 'zip', 'tar', 'tar.gz', 'tar.bz2'. Default is 'zip'.

Returns:
Success message or error description.

### compress_directory
Recursively compress a directory into an archive.

Args:
- `source_dir`: Absolute path to the source directory.
- `archive_path`: Absolute path for the output archive.
- `format`: Archive format, same as above. Default is 'zip'.

Returns:
Success message or error description.

### decompress_archive
Extract an archive to a specified directory. Automatically detects format based on file extension.

Args:
- `archive_path`: Absolute path to the archive file.
- `extract_dir`: Absolute path to the extraction directory (will be created if it doesn't exist).

Returns:
Success message or error description.

### list_archive_contents
List files and directories inside an archive.

Args:
- `archive_path`: Absolute path to the archive file.

Returns:
A formatted list of entries with sizes (for zip) or just names (for tar).

### get_archive_info
Get metadata about an archive: size, compression ratio, number of files, etc.

Args:
- `archive_path`: Absolute path to the archive file.

Returns:
A summary string with archive information.

## Notes

- All paths should be absolute; relative paths are resolved relative to the current working directory of the server.
- The server runs with the same permissions as the agent; it cannot access files outside its permitted scope.
- Large archives may take time; the server will block until the operation completes.