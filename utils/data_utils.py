import csv
import os
import json
import uuid
from models.team import Team
from datetime import datetime
from pymongo import MongoClient


def save_to_mongodb(teams: list, categoria: str):
    """Save teams to MongoDB collection."""
    try:
        # Conectar a MongoDB
        client = MongoClient("mongodb+srv://bebiruesta90:Bebiwing11@mycluster.vheby.mongodb.net/")
        db = client['maristapp']
        collection = db['hockey_team_information']

        updated_count = 0
        inserted_count = 0
        
        # Primero, eliminar todos los equipos de esta categoría para evitar duplicados
        delete_result = collection.delete_many({"categoria": categoria})
        print(f"🗑️ Se eliminaron {delete_result.deleted_count} equipos antiguos de la categoría '{categoria}'")

        # Luego insertar todos los equipos actualizados como nuevos
        teams_to_insert = []
        for team in teams:
            # Crear una copia limpia del equipo
            formatted_team = {
                "Pos": team.get("Pos", ""),
                "Club": team.get("Club", ""),
                "Logo": team.get("Logo", ""),
                "Pts": team.get("Pts", ""),
                "PJ": team.get("PJ", ""),
                "PG": team.get("PG", ""),
                "PE": team.get("PE", ""),
                "PP": team.get("PP", ""),
                "SP": team.get("SP", ""),
                "GF": team.get("GF", ""),
                "GC": team.get("GC", ""),
                "DG": team.get("DG", ""),
                "Bo": team.get("Bo", ""),
                "Sa": team.get("Sa", ""),
                "categoria": categoria,
                "_id": str(uuid.uuid4())  # Generar un nuevo ID para cada equipo
            }
            teams_to_insert.append(formatted_team)

        # Insertar todos los equipos de una vez (más eficiente)
        if teams_to_insert:
            result = collection.insert_many(teams_to_insert)
            inserted_count = len(result.inserted_ids)

        print(f"✅ Se insertaron {inserted_count} equipos en MongoDB para la categoría '{categoria}'")
        
        # Cerrar la conexión
        client.close()
        
    except Exception as e:
        print(f"❌ Error al guardar en MongoDB: {str(e)}")


def is_duplicate_venue(venue_name: str, seen_names: set) -> bool:
    return venue_name in seen_names


def is_complete_venue(venue: dict, required_keys: list) -> bool:
    return all(key in venue for key in required_keys)


def save_failed_urls(failed_urls: list):
    """Save failed URLs to a JSON file."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, "failed_urls.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(failed_urls, f, indent=2, ensure_ascii=False)
    
    print(f"\n⚠️ Se guardaron {len(failed_urls)} URLs fallidas en '{filename}'")


def load_failed_urls() -> list:
    """Load failed URLs from the JSON file."""
    filename = os.path.join("output", "failed_urls.json")
    if not os.path.exists(filename):
        return []
    
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def update_failed_urls(successful_urls: list):
    """Update failed URLs list by removing successful ones."""
    filename = os.path.join("output", "failed_urls.json")
    if not os.path.exists(filename):
        return
    
    # Load current failed URLs
    failed_urls = load_failed_urls()
    
    # Create a set of successful URLs for faster lookup
    successful_set = {(item["categoria"], item["url"]) for item in successful_urls}
    
    # Filter out successful URLs
    updated_failed_urls = [
        item for item in failed_urls 
        if (item["categoria"], item["url"]) not in successful_set
    ]
    
    # Save updated list
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(updated_failed_urls, f, indent=2, ensure_ascii=False)
    
    removed_count = len(failed_urls) - len(updated_failed_urls)
    if removed_count > 0:
        print(f"\n✅ Se removieron {removed_count} URLs exitosas de la lista de fallidas")
    else:
        print("\nℹ️ No se removieron URLs de la lista de fallidas")


def save_teams_to_csv(teams: list, categoria: str):
    if not teams:
        print(f"No teams to save for category {categoria}.")
        return

    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Use field names from the Team model
    fieldnames = Team.model_fields.keys()

    # Limpiar los datos para que solo contengan los campos válidos
    cleaned_teams = []
    for team in teams:
        cleaned_team = {key: value for key, value in team.items() if key in fieldnames}
        cleaned_teams.append(cleaned_team)

    # Create filename based on category
    filename = os.path.join(output_dir, f"tabla_hockey_{categoria.lower().replace(' ', '_')}.csv")

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_teams)

    print(f"Saved {len(cleaned_teams)} teams for category '{categoria}' to '{filename}'.")
    print(f"Fields saved: {', '.join(fieldnames)}")

