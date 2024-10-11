from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, HeroPower, Power

app = Flask(__name__)

# Set up the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///superheroes.db'
db.init_app(app)
Migrate(app, db)

@app.route('/')
def index():
    """Return a welcome message indicating the API is live."""
    return '''
        <h1>Superheroes API</h1>
        <p>This API lets you track superheroes and their powers.</p>
        <h2><code>GET /heroes</code></h2>
        <p>Get a list of all heroes.</p>
        <h2><code>GET /heroes/&lt;id&gt;</code></h2>
        <p>Get details for a specific hero.</p>
        <h2><code>GET /powers</code></h2>
        <p>Get a list of all available powers.</p>
        <h2><code>GET /powers/&lt;id&gt;</code></h2>
        <p>Get details of a specific power.</p>
        <h2><code>PATCH /powers/&lt;id&gt;</code></h2>
        <p>Update a power's details.</p>
        <h2><code>POST /hero_powers</code></h2>
        <p>Create a new hero-power relationship.</p>
    '''

@app.route('/heroes', methods=['GET'])
def get_heroes():
    """Get a list of all heroes."""
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes])

@app.route('/heroes/<int:id>', methods=['GET'])
def hero_by_id(id):
    """Get a hero by their ID."""
    hero = Hero.query.get(id)
    if not hero:
        return {'error': 'Hero not found'}, 404
    return hero.to_dict()

@app.route('/powers', methods=['GET'])
def get_powers():
    """Get a list of all powers."""
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers])

@app.route('/hero_powers', methods=['POST'])  
def hero_powers():
    """Create a new hero-power relationship."""
    
    
    data = request.json
    print(f"Received data: {data}")  

    if data is None:
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    # Extract fields with validation
    strength = data.get('strength')
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')

    if strength is None or hero_id is None or power_id is None:
        return jsonify({'error': 'Missing required fields: strength, hero_id, power_id'}), 400

    
    normalized_strength = strength.title()

    valid_strengths = ['Strong', 'Weak', 'Average']
    if normalized_strength not in valid_strengths:
        return jsonify({'error': f'Strength must be one of {valid_strengths}.'}), 400

    try:
        # Create a new HeroPower 
        new_hero_power = HeroPower(
            strength=normalized_strength,
            power_id=power_id,
            hero_id=hero_id
        )
        db.session.add(new_hero_power)
        db.session.commit()

        return jsonify(new_hero_power.to_dict()), 201
    except ValueError as e:
        print(f"ValueError: {str(e)}")  
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()  
        print(f"Exception: {str(e)}")  
        return jsonify({'error': ['Validation errors', str(e)]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)