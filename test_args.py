def _build_summary_items(
    view,
    start_date,
    end_date,
    punches,
    time_off_map,
    time_off_requests_map,
    overtime_daily,
    tzinfo,
):
    pass

try:
    _build_summary_items(
        view=1,
        start_date=2,
        end_date=3,
        punches=4,
        time_off_map=5,
        time_off_requests_map=6,
        overtime_daily=7,
        tzinfo=8,
    )
    print("SUCCESS")
except TypeError as ex:
    print("ERROR:", repr(ex))
