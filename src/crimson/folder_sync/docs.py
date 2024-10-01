def with_docs(func, meta, render):
    pass


with_docs(
    func=print,
    meta={
        "summary": "It watches the source_dir, and move the files if changes are detected.",
        "description": {
            "How to use": """\
                Check [syncer.ipynb](example/folder_sync/syncer.ipynb) and\
                [example.ipynb](example/folder_sync/example.ipynb)
                """,
            "Patterns": """\
                The patterns of path to be synced determined by include and exclude. To understand 
                """
        }
    },
    render=print
)
