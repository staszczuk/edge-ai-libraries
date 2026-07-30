# How to add a new element

ViPPET does not implement its own GStreamer elements. The pipeline editor
exposes every element that appears in a pipeline definition, both the
standard GStreamer/DL Streamer elements (`filesrc`, `decodebin3`, `queue`,
`gvadetect`, `gvaclassify`, `gvatrack`, `gvawatermark`, `gvametaconvert`,
`gvametapublish`, ...) and any custom Python module loaded through
`gvapython`. If the element is already provided by the base image, it is
enough to reference it in a pipeline (see
[How to add a new pipeline](./new-pipeline.md)) to make it show up in the
editor. This page focuses on the three extension points contributors
actually have:

1. Shipping a GStreamer plugin that is **not** part of the base image and
   giving it a proper node in the pipeline editor.
2. Loading custom Python scripts through the `gvapython` element.
3. Controlling whether an element is visible in the simplified pipeline view.

## Add an element that is not in the base image

The `gencamsrc` and `pylonsrc` camera sources, added for the proof-of-concept
Basler GigE Vision support, are a complete reference implementation. Follow the
same steps:

1. **Install the plugin** in the `prod` stage of `vippet/Dockerfile`, either
   built from sources or from a package. Keep anything that noticeably grows the
   image or depends on a vendor SDK behind a build argument that defaults to
   *off*, and forward that argument in `compose.yml` and `setup_env.sh`.
2. **Make the plugin discoverable**: add its install directory to
   `GST_PLUGIN_PATH` and set any environment variable the vendor SDK needs at
   runtime. Verify with `gst-inspect-1.0 <element>` inside `make shell`.
3. **Declare runtime requirements**, if any. Extra devices, volumes or networks
   belong in `compose.yml`, with host-specific values kept in `setup_env.sh`.
4. **Reference the element from a pipeline** under `vippet/pipelines/` - an
   element only becomes reachable from the UI once a pipeline uses it. See
   [How to add a new pipeline](./new-pipeline.md).
5. **Add a node component** in `ui/src/features/pipeline-editor/nodes/` and
   register it in `nodes/index.ts` under the exact GStreamer element name.
   Without it the editor falls back to a plain default box.
6. **Validate and document**: run `make lint`, `make test` and `make build run`,
   check the element in both the Advanced and the Simple view, and describe any
   new build argument or environment variable in the README,
   [`AGENTS.md`](https://github.com/open-edge-platform/edge-ai-libraries/blob/main/tools/visual-pipeline-and-platform-evaluation-tool/AGENTS.md)
   and, when it is user facing, in the user documentation.

## Use custom `gvapython` modules (deprecated)

The `shared/scripts` directory contains user-defined Python scripts that
can be loaded as modules by the `gvapython` element.

To add and use a new script:

1. Drop your script into `shared/scripts` (for example
   `tracked_object_filter.py`).
2. In your pipeline description, set the `module` property on the
   `gvapython` element to the script filename.
   Example: `gvapython module=tracked_object_filter.py`.

No additional effort is needed, referencing the filename via `module` is
sufficient after the file is placed in this directory. The backend resolves
the filename to an absolute container path
(`/scripts/<file>.py`) when building the runnable pipeline command, and
maps it back to the bare filename when storing the graph.

> **Note:** The `shared/scripts` directory is excluded from linter checks, as it
> contains custom scripts that may not conform to standard linting rules.

### Limitations

Passing values to the `kwarg` property of the `gvapython` element in the
pipeline is not supported.

**Example of unsupported usage:**

```text
gvapython class=ObjectFilter module=tracked_object_filter.py kwarg="{\"reclassify_interval\": $BARCODE_RECLASSIFY_INTERVAL}"
```

## Element visibility in the simple view

The pipeline editor offers two views of every variant:

- **Advanced view**: the full graph, with every element and every caps
  filter, exactly as stored.
- **Simple view**: a curated subset that hides technical plumbing
  (queues, converters, demuxers, caps ...) and focuses on
  sources, inference and sinks.

The Simple view is computed by `Graph.to_simple_view()` in
`vippet/graph.py` and is driven by two environment variables, both
configured on the `vippet` service in `compose.yml`:

| Variable                         | Default                                                    | Meaning                                                                                                              |
|----------------------------------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `SIMPLE_VIEW_VISIBLE_ELEMENTS`   | `*src,urisourcebin,gva*,*sink,source`                      | Comma-separated wildcard patterns. An element is a candidate for the Simple view only if its type matches one entry. |
| `SIMPLE_VIEW_INVISIBLE_ELEMENTS` | `gvafpscounter,gvametapublish,gvametaconvert,gvawatermark` | Comma-separated wildcard patterns. Matches are removed from the Simple view even if they also match the visible set. |

Evaluation order is **VISIBLE first, then INVISIBLE exclusions**. Caps nodes
(internal `__node_kind=caps`) are always hidden in the Simple view.

When introducing a new element (typically by writing a new pipeline that
references it):

- If the element is a meaningful, user-facing step (a new source family,
  a new inference element following the `gva*` naming, a new sink...) it
  will appear in the Simple view automatically thanks to the default
  patterns.
- If the element is purely technical plumbing (a new converter, a new
  parser, a buffering element...) and you do not want it on the Simple
  view, add it to `SIMPLE_VIEW_INVISIBLE_ELEMENTS` in `compose.yml`.
- If your element name does not match any of the existing patterns
  (for example it is not `*src` / `gva*` / `*sink` / `urisourcebin` /
  `source`) and should be exposed, extend `SIMPLE_VIEW_VISIBLE_ELEMENTS`
  accordingly. Keep the patterns broad and named, not pipeline-specific.

Any change to these variables must also be documented in the README and
in the *Key Environment Variables* table of
[`AGENTS.md`](https://github.com/open-edge-platform/edge-ai-libraries/blob/main/tools/visual-pipeline-and-platform-evaluation-tool/AGENTS.md).

## Related pages

- [How to add a new pipeline](./new-pipeline.md)
- [Backend contributing guide](./backend.md)
