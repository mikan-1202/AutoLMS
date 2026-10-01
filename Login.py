"""従来と同じ起動コマンドを維持する入口。"""

from lms_login.app import main

if __name__ == "__main__":
    raise SystemExit(main())
