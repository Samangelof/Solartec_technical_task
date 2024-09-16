from bot import create_app


app = create_app()

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 4042
    print(f"Server on http://{host}:{port}")
    app.run(debug=True, host=host, port=port)