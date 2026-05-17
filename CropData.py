def crop_data(data, delta_start, delta_end):
    old_start_epoch = data["meta"]["start_epoch"]

    new_start_epoch = old_start_epoch + delta_start
    new_end_epoch = old_start_epoch + delta_end

    # helper functions
    def crop_gps(signal):
        mask = [
            (new_start_epoch <= epoch <= new_end_epoch)
            for epoch in signal["epoch"]
        ]

        cropped_signal = {
            k: [v[i] for i, m in enumerate(mask) if m]
            for k, v in signal.items()
        }
        return cropped_signal

    def crop_time_signal(signal):
        t = signal["time"]

        mask = [
            (delta_start <= ti <= delta_end)
            for ti in t
        ]

        cropped_signal = {
            k: [v[i] for i, m in enumerate(mask) if m]
            for k, v in signal.items()
        }

        if len(cropped_signal["time"]) > 0:
            t0 = cropped_signal["time"][0]
            cropped_signal["time"] = [ti - t0 for ti in cropped_signal["time"]]

        return cropped_signal

    # build cropped dataset
    cropped = {
        "gps": crop_gps(data["gps"]),
        "accel": crop_time_signal(data["accel"]),
        "gyro": crop_time_signal(data["gyro"]),
        "rotation": crop_time_signal(data["rotation"]),
        "meta": {
            "start_epoch": new_start_epoch,
            "end_epoch": new_end_epoch,
            "duration": delta_end - delta_start
        }
    }

    return cropped