def crop_data(data, delta_start, delta_end):
    old_start_time = data["meta"]["start_time"]
    new_start_time = old_start_time + delta_start
    new_end_time = old_start_time + delta_end

    # helper function
    def crop_signal(signal):
        t = signal["time"]

        mask = [(new_start_time <= ti <= new_end_time) for ti in t]

        return {
            k: [v[i] for i, m in enumerate(mask) if m]
            for k, v in signal.items()
        }

    cropped = {
        "gps": crop_signal(data["gps"]),
        "accel": crop_signal(data["accel"]),
        "gyro": crop_signal(data["gyro"]),
        "sensor4": crop_signal(data["sensor4"]),
        "meta": {
            "start_time": new_start_time,
            "end_time": new_end_time,
            "duration": delta_end - delta_start
        }
    }

    return cropped