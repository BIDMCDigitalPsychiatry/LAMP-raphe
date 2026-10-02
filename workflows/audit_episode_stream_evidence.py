from pathlib import Path

import pandas as pd

from raphe.io.source_index import SourceFileIndex


EPISODES_PATH = Path(
    "../raphe_outputs/digital_clinic/"
    "inventory/episodes.parquet"
)

MANIFEST_DIR = Path(
    "../raphe_outputs/digital_clinic/"
    "inventory/source_files"
)

OUTPUT_PATH = Path(
    "../raphe_outputs/digital_clinic/"
    "quality/episode_stream_evidence.csv"
)

STREAMS = [
    "gps",
    "accelerometer",
    "screen",
]


episodes = pd.read_parquet(
    EPISODES_PATH
)

index = SourceFileIndex(
    MANIFEST_DIR
)

rows = []


for ep in episodes.itertuples(
    index=False
):

    for stream in STREAMS:

        files = index.candidate_records(
            stream,
            source_participant_id=(
                ep.source_participant_id
            ),
            start_ms=int(ep.start_ms),
            end_ms=int(ep.end_ms),
            verify_files=False,
        )

        has_stream_evidence = (
            len(files) > 0
        )

        rows.append({
            "participant_id":
                str(ep.participant_id),

            "episode_id":
                str(ep.episode_id),

            "source_participant_id":
                str(
                    ep.source_participant_id
                ),

            "stream":
                stream,

            "episode_start_ms":
                int(ep.start_ms),

            "episode_end_ms":
                int(ep.end_ms),

            "overlapping_files":
                int(len(files)),

            "overlapping_bytes":
                int(
                    files[
                        "size_bytes"
                    ].sum()
                )
                if len(files)
                else 0,

            "has_stream_evidence":
                bool(
                    has_stream_evidence
                ),

            "observed_min_ms":
                (
                    int(
                        files[
                            "min_timestamp_ms"
                        ].min()
                    )
                    if len(files)
                    else None
                ),

            "observed_max_ms":
                (
                    int(
                        files[
                            "max_timestamp_ms"
                        ].max()
                    )
                    if len(files)
                    else None
                ),
        })


out = pd.DataFrame(
    rows
)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

out.to_csv(
    OUTPUT_PATH,
    index=False,
)


print(
    "Rows:",
    len(out)
)

print(
    "Episodes:",
    out["episode_id"].nunique()
)

print("\nStream evidence:")

summary = (
    out.groupby("stream")
    .agg(
        episodes=(
            "episode_id",
            "size",
        ),
        episodes_with_evidence=(
            "has_stream_evidence",
            "sum",
        ),
        total_overlapping_files=(
            "overlapping_files",
            "sum",
        ),
    )
)

summary[
    "episodes_without_evidence"
] = (
    summary["episodes"]
    - summary[
        "episodes_with_evidence"
    ]
)

summary[
    "fraction_with_evidence"
] = (
    summary[
        "episodes_with_evidence"
    ]
    / summary["episodes"]
)

print(
    summary.to_string()
)


wide = (
    out.pivot(
        index="episode_id",
        columns="stream",
        values="has_stream_evidence",
    )
    .fillna(False)
)

wide["all_three"] = (
    wide["gps"]
    & wide["accelerometer"]
    & wide["screen"]
)

wide["none"] = ~(
    wide["gps"]
    | wide["accelerometer"]
    | wide["screen"]
)

print(
    "\nEpisode overlap:"
)

print(
    "All three streams:",
    int(
        wide["all_three"].sum()
    ),
)

print(
    "No evidence for any of three:",
    int(
        wide["none"].sum()
    ),
)

print(
    "\nCombination counts:"
)

print(
    wide[
        [
            "gps",
            "accelerometer",
            "screen",
        ]
    ]
    .value_counts()
    .to_string()
)

print("\nSaved:")
print(OUTPUT_PATH)
