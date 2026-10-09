import numpy as np
import pandas as pd


HOUR_MS = 3_600_000


def _hour_grid(
    reader,
    episode_id,
):
    ep = reader.episode(
        episode_id
    )

    start = int(
        ep["start_ms"]
    )

    end = int(
        ep["end_ms"]
    )

    starts = np.arange(
        start,
        end,
        HOUR_MS,
        dtype=np.int64,
    )

    ends = np.minimum(
        starts + HOUR_MS,
        end,
    )

    return ep, starts, ends


def _hour_index(
    timestamps,
    *,
    episode_start,
    n_hours,
):
    h = (
        (
            timestamps
            - episode_start
        )
        // HOUR_MS
    ).astype(np.int64)

    valid = (
        (h >= 0)
        &
        (h < n_hours)
    )

    return h, valid


def episode_hourly_context(
    reader,
    *,
    episode_id,
    stream_evidence,
    chunksize=1_000_000,
):
    """
    Build positive hourly contextual evidence.

    Missing contextual records are not interpreted as behavioral
    zeros or sensor failure.
    """

    ep, starts, ends = _hour_grid(
        reader,
        episode_id,
    )

    episode_start = int(
        ep["start_ms"]
    )

    n_hours = len(starts)

    out = pd.DataFrame({
        "participant_id":
            str(ep["participant_id"]),

        "episode_id":
            str(ep["episode_id"]),

        "source_participant_id":
            str(
                ep[
                    "source_participant_id"
                ]
            ),

        "hour_index":
            np.arange(
                n_hours,
                dtype=np.int64,
            ),

        "start_ms":
            starts,

        "end_ms":
            ends,

        "hour_start_utc":
            pd.to_datetime(
                starts,
                unit="ms",
                utc=True,
            ),

        "hour_end_utc":
            pd.to_datetime(
                ends,
                unit="ms",
                utc=True,
            ),
    })

    # ========================================================
    # SCREEN + BATTERY
    # ========================================================

    screen_event_count = np.zeros(
        n_hours,
        dtype=np.int64,
    )

    battery_count = np.zeros(
        n_hours,
        dtype=np.int64,
    )

    battery_sum = np.zeros(
        n_hours,
        dtype=float,
    )

    battery_min = np.full(
        n_hours,
        np.nan,
    )

    battery_max = np.full(
        n_hours,
        np.nan,
    )

    battery_first = np.full(
        n_hours,
        np.nan,
    )

    battery_last = np.full(
        n_hours,
        np.nan,
    )

    battery_first_ts = np.full(
        n_hours,
        np.iinfo(np.int64).max,
        dtype=np.int64,
    )

    battery_last_ts = np.full(
        n_hours,
        np.iinfo(np.int64).min,
        dtype=np.int64,
    )

    has_screen = bool(
        stream_evidence.get(
            "screen",
            False,
        )
    )

    if has_screen:

        for chunk in reader.iter_stream(
            "screen",
            episode_id=episode_id,
            chunksize=chunksize,
        ):

            ts = pd.to_numeric(
                chunk["timestamp_ms"],
                errors="coerce",
            )

            valid_ts = ts.notna()

            if not valid_ts.any():
                continue

            z = chunk.loc[
                valid_ts
            ].copy()

            t = ts.loc[
                valid_ts
            ].astype(
                "int64"
            ).to_numpy()

            h, valid = _hour_index(
                t,
                episode_start=episode_start,
                n_hours=n_hours,
            )

            z = z.iloc[
                np.flatnonzero(valid)
            ]

            t = t[valid]
            h = h[valid]

            screen_event_count += (
                np.bincount(
                    h,
                    minlength=n_hours,
                )
            )

            if (
                "battery_level_fraction"
                not in z.columns
            ):
                continue

            battery = pd.to_numeric(
                z[
                    "battery_level_fraction"
                ],
                errors="coerce",
            ).to_numpy()

            bvalid = np.isfinite(
                battery
            )

            for hour in np.unique(
                h[bvalid]
            ):

                mask = (
                    (h == hour)
                    &
                    bvalid
                )

                values = battery[
                    mask
                ]

                times = t[
                    mask
                ]

                battery_count[
                    hour
                ] += len(values)

                battery_sum[
                    hour
                ] += values.sum()

                vmin = float(
                    values.min()
                )

                vmax = float(
                    values.max()
                )

                if np.isnan(
                    battery_min[hour]
                ):
                    battery_min[
                        hour
                    ] = vmin
                    battery_max[
                        hour
                    ] = vmax

                else:
                    battery_min[
                        hour
                    ] = min(
                        battery_min[
                            hour
                        ],
                        vmin,
                    )

                    battery_max[
                        hour
                    ] = max(
                        battery_max[
                            hour
                        ],
                        vmax,
                    )

                first_i = int(
                    np.argmin(times)
                )

                last_i = int(
                    np.argmax(times)
                )

                if (
                    times[first_i]
                    < battery_first_ts[
                        hour
                    ]
                ):
                    battery_first_ts[
                        hour
                    ] = times[
                        first_i
                    ]

                    battery_first[
                        hour
                    ] = values[
                        first_i
                    ]

                if (
                    times[last_i]
                    > battery_last_ts[
                        hour
                    ]
                ):
                    battery_last_ts[
                        hour
                    ] = times[
                        last_i
                    ]

                    battery_last[
                        hour
                    ] = values[
                        last_i
                    ]

    battery_mean = np.full(
        n_hours,
        np.nan,
    )

    b = battery_count > 0

    battery_mean[b] = (
        battery_sum[b]
        /
        battery_count[b]
    )

    out[
        "screen_episode_evidence"
    ] = has_screen

    out[
        "screen_event_count"
    ] = screen_event_count

    out[
        "screen_event_observed"
    ] = (
        screen_event_count > 0
    )

    out[
        "battery_observation_count"
    ] = battery_count

    out[
        "battery_mean"
    ] = battery_mean

    out[
        "battery_min"
    ] = battery_min

    out[
        "battery_max"
    ] = battery_max

    out[
        "battery_first"
    ] = battery_first

    out[
        "battery_last"
    ] = battery_last

    out[
        "battery_within_hour_delta"
    ] = (
        battery_last
        - battery_first
    )


    # ========================================================
    # DEVICE USAGE
    # ========================================================

    device_records = np.zeros(
        n_hours,
        dtype=np.int64,
    )

    duration_sum = np.zeros(
        n_hours,
        dtype=float,
    )

    unlock_duration_sum = np.zeros(
        n_hours,
        dtype=float,
    )

    unlocks_sum = np.zeros(
        n_hours,
        dtype=float,
    )

    wakes_sum = np.zeros(
        n_hours,
        dtype=float,
    )

    has_device_usage = bool(
        stream_evidence.get(
            "device_usage",
            False,
        )
    )

    if has_device_usage:

        for chunk in reader.iter_stream(
            "device_usage",
            episode_id=episode_id,
            chunksize=chunksize,
        ):

            ts = pd.to_numeric(
                chunk["timestamp_ms"],
                errors="coerce",
            )

            valid_ts = ts.notna()

            if not valid_ts.any():
                continue

            z = chunk.loc[
                valid_ts
            ].copy()

            t = ts.loc[
                valid_ts
            ].astype(
                "int64"
            ).to_numpy()

            h, valid = _hour_index(
                t,
                episode_start=episode_start,
                n_hours=n_hours,
            )

            z = z.iloc[
                np.flatnonzero(valid)
            ]

            h = h[valid]

            device_records += (
                np.bincount(
                    h,
                    minlength=n_hours,
                )
            )

            mappings = [
                (
                    "interval_duration_ms",
                    duration_sum,
                ),
                (
                    "total_unlock_duration_ms",
                    unlock_duration_sum,
                ),
                (
                    "total_unlocks",
                    unlocks_sum,
                ),
                (
                    "total_screen_wakes",
                    wakes_sum,
                ),
            ]

            for column, target in mappings:

                if column not in z.columns:
                    continue

                values = pd.to_numeric(
                    z[column],
                    errors="coerce",
                ).fillna(
                    0
                ).to_numpy(
                    dtype=float
                )

                target += np.bincount(
                    h,
                    weights=values,
                    minlength=n_hours,
                )

    no_device_record = (
        device_records == 0
    )

    for values in [
        duration_sum,
        unlock_duration_sum,
        unlocks_sum,
        wakes_sum,
    ]:
        values[
            no_device_record
        ] = np.nan

    out[
        "device_usage_episode_evidence"
    ] = has_device_usage

    out[
        "device_usage_record_count"
    ] = device_records

    out[
        "device_usage_observed"
    ] = (
        device_records > 0
    )

    out[
        "device_reported_duration_ms"
    ] = duration_sum

    out[
        "unlock_duration_ms"
    ] = unlock_duration_sum

    out[
        "unlock_count"
    ] = unlocks_sum

    out[
        "screen_wake_count"
    ] = wakes_sum


    # ========================================================
    # NEARBY DEVICE
    # ========================================================

    nearby_records = np.zeros(
        n_hours,
        dtype=np.int64,
    )

    wifi_records = np.zeros(
        n_hours,
        dtype=np.int64,
    )

    bluetooth_records = np.zeros(
        n_hours,
        dtype=np.int64,
    )

    unique_all = [
        set()
        for _ in range(n_hours)
    ]

    unique_wifi = [
        set()
        for _ in range(n_hours)
    ]

    unique_bluetooth = [
        set()
        for _ in range(n_hours)
    ]

    has_nearby = bool(
        stream_evidence.get(
            "nearby_device",
            False,
        )
    )

    if has_nearby:

        for chunk in reader.iter_stream(
            "nearby_device",
            episode_id=episode_id,
            chunksize=chunksize,
        ):

            ts = pd.to_numeric(
                chunk["timestamp_ms"],
                errors="coerce",
            )

            valid_ts = ts.notna()

            if not valid_ts.any():
                continue

            z = chunk.loc[
                valid_ts
            ].copy()

            t = ts.loc[
                valid_ts
            ].astype(
                "int64"
            ).to_numpy()

            h, valid = _hour_index(
                t,
                episode_start=episode_start,
                n_hours=n_hours,
            )

            z = z.iloc[
                np.flatnonzero(valid)
            ].reset_index(
                drop=True
            )

            h = h[valid]

            nearby_records += (
                np.bincount(
                    h,
                    minlength=n_hours,
                )
            )

            types = (
                z["device_type"]
                .astype("string")
                .str.lower()
                if "device_type" in z
                else pd.Series(
                    [None] * len(z)
                )
            )

            ids = (
                z[
                    "nearby_identifier_hash"
                ]
                if (
                    "nearby_identifier_hash"
                    in z
                )
                else pd.Series(
                    [None] * len(z)
                )
            )

            for i, hour in enumerate(h):

                typ = types.iloc[i]

                ident = ids.iloc[i]

                if typ == "wifi":
                    wifi_records[
                        hour
                    ] += 1

                elif typ == "bluetooth":
                    bluetooth_records[
                        hour
                    ] += 1

                if pd.notna(ident):

                    unique_all[
                        hour
                    ].add(
                        str(ident)
                    )

                    if typ == "wifi":
                        unique_wifi[
                            hour
                        ].add(
                            str(ident)
                        )

                    elif typ == "bluetooth":
                        unique_bluetooth[
                            hour
                        ].add(
                            str(ident)
                        )

    out[
        "nearby_device_episode_evidence"
    ] = has_nearby

    out[
        "nearby_record_count"
    ] = nearby_records

    out[
        "nearby_observation_present"
    ] = (
        nearby_records > 0
    )

    out[
        "wifi_record_count"
    ] = wifi_records

    out[
        "bluetooth_record_count"
    ] = bluetooth_records

    out[
        "unique_nearby_id_count"
    ] = [
        len(x)
        for x in unique_all
    ]

    out[
        "unique_wifi_id_count"
    ] = [
        len(x)
        for x in unique_wifi
    ]

    out[
        "unique_bluetooth_id_count"
    ] = [
        len(x)
        for x in unique_bluetooth
    ]

    return out
