from application import create_app


"""

Creates our web pp and registers routes/blueprints.

"""
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

    from application.main.routes import main 
    app.register_blueprint(main)