from flask import Flask


def register_routes(app: Flask):
    # import and register blueprints here
    from app.blueprints.hello_world import bp

    app.register_blueprint(bp)

    return app
