# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Sphinx Tutorial ---------------------------------------------------------
# The following Video by Juan Luis Cano Rodríguez offers the best Sphinx tutorial I have found so far:
#
# https://www.youtube.com/watch?v=qRSb299awB0
#
# This configuration file is based on the tutorial video.
# Give Juan Luis Cano Rodríguez a like and subscribe to his channel if you like. I think he deserves it.


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BluePrints'
copyright = '2024, WZL IQS Aachen'
author = 'Alexander Nasuta, Mats Gesenhues'
release = '0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'nbsphinx',  # allows to include jupyter notebooks, alternative: 'MyST-NB'

    'sphinx.ext.duration',  # built-in -> shows duration build time per file
    'sphinx.ext.autosectionlabel',  # built-in -> allows to reference sections with :ref: directive
    # comment in if needed
    # 'sphinx.ext.napoleon', # built-in -> allows to use numpy-style docstrings and google-style docstrings

    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary', # alternative: 'sphinx.ext.autoapi' <- NOTE:  try this
    'sphinx.ext.autosectionlabel',

    'sphinx_copybutton'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# other themes available under https://sphinx-themes.org/
html_theme = 'furo'  # looks cooler than 'alabaster' (gives cool dark mode too
html_static_path = ['_static']
html_css_files = ['custom.css']

html_logo = '_static/logo-optipack.svg'

copybutton_prompt_text = ">>> "
copybutton_prompt_is_regexp = False
