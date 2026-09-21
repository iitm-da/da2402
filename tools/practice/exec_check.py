"""Execute a worksheet with its remote data URL swapped for a local folder."""
import sys, os
import nbformat
from nbclient import NotebookClient

src, remote, local = sys.argv[1], sys.argv[2], sys.argv[3]
nb = nbformat.read(src, as_version=4)
for c in nb.cells:
    if c.cell_type == "code":
        c.source = c.source.replace(remote, local)
NotebookClient(nb, timeout=180, kernel_name="python3",
               resources={"metadata": {"path": os.path.dirname(os.path.abspath(src))}}).execute()
print("executed ok:", src)
