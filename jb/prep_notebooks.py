import nbformat as nbf
import yaml
from glob import glob

# Page descriptions for search results and link previews
with open('descriptions.yml') as f:
    DESCRIPTIONS = yaml.safe_load(f)


def process_cell(cell):
    # get tags
    tags = cell['metadata'].get('tags', [])

    # add hide-cell tag to solutions
    if cell['cell_type'] == 'code':
        source = cell['source']

        # remove solutions
        if source.startswith('# Solution') or 'solution' in tags:
            cell['source'] = []

        # remove %%expect cell magic
        if source.startswith('%%expect'):
            t = source.split('\n')[1:]
            cell['source'] = '\n'.join(t)

    # add reference label
    for tag in tags:
        if tag.startswith('chapter') or tag.startswith('section'):
            print(tag)
            label = f'({tag})=\n'
            cell['source'] = label + cell['source']


def process_notebook(path):
    ntbk = nbf.read(path, nbf.NO_CONVERT)

    for cell in ntbk.cells:
        process_cell(cell)

    nbf.write(ntbk, path)


def add_description(path):
    """Write the page description into the notebook metadata.

    myst-nb passes notebook metadata through as front matter: html_meta becomes
    <meta name="description">; og:description overrides the link-preview text,
    which would otherwise be the ordering paragraph.
    """
    desc = DESCRIPTIONS.get(path.removesuffix('.ipynb'))
    if not desc:
        print('no description for', path)
        return
    ntbk = nbf.read(path, nbf.NO_CONVERT)
    ntbk.metadata['myst'] = {'html_meta': {'description': desc}}
    ntbk.metadata['og:description'] = desc
    nbf.write(ntbk, path)


# Collect a list of the notebooks in the content folder
paths = glob("chap*.ipynb")

for path in sorted(paths):
    print('prepping', path)
    process_notebook(path)

# Descriptions for the chapters and the examples
for path in sorted(glob("*.ipynb")):
    add_description(path)
