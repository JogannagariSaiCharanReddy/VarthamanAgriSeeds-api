from fastapi import FastAPI, Request # Import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import pathlib

app = FastAPI()

# --- 1. MOUNT STATIC FILES ---
# This is the most important change. It tells FastAPI to create a public URL
# at "/static" that serves the files from your "static" directory.
app.mount("/static", StaticFiles(directory="static"), name="static")


# Configure CORS (Your configuration is fine for now)
origins = [
    "https://JogannagariSaiCharanReddy.github.io", # IMPORTANT: Change this later
    "http://varthamanagriseeds.info",
    "https://varthamanagriseeds.info",
    "http://www.varthamanagriseeds.info",
    "https://www.varthamanagriseeds.info",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# This function now correctly builds a public URL, not a local file path
async def add_img_url(crop_type_list: list, request: Request):
    # Get the base URL of your API (e.g., "https://your-api.onrender.com/")
    base_url = str(request.base_url)

    for crop_type in crop_type_list:
        # Construct the file name from the crop name
        base_filename = crop_type["name"].replace(" ", "_")
        found_image = False
        
        # Check for different possible extensions
        for extension in [".jpg", ".jpeg", ".webp", ".png"]:
            image_path = pathlib.Path(f"static/images/{base_filename}{extension}")
            if image_path.exists():
                # If the file exists, build the FULL public URL
                crop_type["image_url"] = f"{base_url}{str(image_path).replace('\\', '/')}"
                found_image = True
                break
        
        if not found_image:
            # Fallback if no image is found
            crop_type["image_url"] = "https://placehold.co/600x400/cccccc/ffffff?text=Image+Not+Found"
            
    return crop_type_list

# Load the JSON data (This part is good, no changes needed)
with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'r') as file:
    data = json.load(file)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Varthaman Agri Seeds API"}

@app.get("/api/company-profile")
def get_company_profile():
    return data.get("company_profile", {})

# --- 2. CORRECTED LOGO URL ---
# This now returns a relative URL that your frontend can use.
# The frontend will combine it with the API_BASE_URL.
@app.get("/api/logo")
async def get_logo(request: Request):
    # The URL is now constructed dynamically and correctly
    logo_url = str(request.base_url) + "static/logo.png"
    return {"logo_url": logo_url}


@app.get("/api/categories")
async def get_crop_categories():
    return [category for category in data.get("crop_data",{})]

@app.get("/api/crops")
async def get_all_crops():
    return data.get("crop_data", {})

# --- 3. CORRECTED CROP DATA ENDPOINT ---
# It now accepts the `Request` object to build the proper image URLs.
@app.get("/api/crops/{crop_name}")
async def get_crop_by_name(crop_name: str, request: Request): # Pass request here
    crop_list = data.get("crop_data", {}).get(crop_name, []) # Use [] as default
    crop_list_with_img_url = await add_img_url(crop_list, request) # Pass request
    return crop_list_with_img_url

@app.get("/healthz")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
