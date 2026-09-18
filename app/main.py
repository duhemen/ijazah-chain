import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from app.config import MODE, APP_NAME, APP_VERSION
from app.ui.main_window import MainWindow


def get_blockchain():
    """
    Return instance blockchain sesuai MODE.
    Jika server mode gagal, fallback ke local dengan konfirmasi user.
    """
    if MODE == "server":
        from app.network.api_client import RemoteBlockchain, ApiError
        try:
            rb = RemoteBlockchain()
            rb.refresh_chain()  # test koneksi + load initial chain
            print(f"[MODE] Server @ {rb.server_url}  (API key: {rb.api_key[:8]}...)")
            return rb
        except ApiError as e:
            print(f"[MODE] Server error: {e}")
            reply = QMessageBox.question(
                None,
                "Server Tidak Tersedia",
                f"Gagal terhubung ke server:\n\n{e}\n\n"
                f"Jalankan aplikasi dalam mode LOCAL (offline)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.No:
                sys.exit(0)

    from app.blockchain.storage import load_blockchain_from_db
    print("[MODE] Local SQLite")
    return load_blockchain_from_db()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(f"{APP_NAME} v{APP_VERSION}")

    blockchain = get_blockchain()

    window = MainWindow(blockchain)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()