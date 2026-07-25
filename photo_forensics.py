from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from PIL.ExifTags import TAGS
from PIL import Image
from pillow_heif import register_heif_opener

import sys
import time
import os
import hashlib

register_heif_opener()
console = Console()

SUPPORTED = (
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp",
    ".heic",
    ".heif"
)

console.print(
    Panel.fit(
        "[bold cyan]PHOTO FORENSICS TOOL[/bold cyan]\n"
        "[green]Version 1.0.0[/green]\n"
        "Developer: [bold yellow]TrXiNo[/bold yellow]",
        border_style="cyan"
    )
)

#region file_information
def file_information(path):
    img = Image.open(path)
    print()
    table = Table(title="File Information")
    table.add_column("Property")
    table.add_column("Value")
    table.add_row("Filename", os.path.basename(path))
    table.add_row("Format", img.format)
    table.add_row("Resolution", f"{img.width} x {img.height}")
    table.add_row("Color Mode", img.mode)
    table.add_row("Size", f"{os.path.getsize(path)/1024:.2f} KB")
    table.border_style = "cyan"
    console.print(table)
#endregion

#region exif_information
def exif_information(path):
    img = Image.open(path)
    exif = img.getexif()
    table = Table(title="EXIF Metadata")
    table.add_column("Tag")
    table.add_column("Value")
    table.border_style = "cyan"
    if not exif:
        console.print("[red]\nNo EXIF metadata found.\n[/red]")
        return
    TAGS[59932] = "ImageUniqueID"
    for tag, value in exif.items():
        tag = TAGS.get(tag, tag)
        table.add_row(str(tag), str(value))
    console.print(table)
#endregion

#region sha256
def sha256(path):
    h = hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            h.update(data)

    table = Table(title="File Hash")
    table.add_column("Algorithm")
    table.add_column("Hash")
    table.add_row("SHA256", h.hexdigest())
    table.border_style = "cyan"
    console.print(table)
#endregion

#region camera_information
def camera_information(path):
    img = Image.open(path)
    exif = img.getexif()
    make = exif.get(271,"Not Available")
    model = exif.get(272,"Not Available")
    software = exif.get(305,"Not Available")
    image_unique_id = exif.get(59932,"Not Available")
    table = Table(title="Camera")
    table.add_column("Information")
    table.add_column("Value")
    table.add_row("Manufacturer",str(make))
    table.add_row("Model",str(model))
    table.add_row("Software",str(software))
    table.border_style = "cyan"
    console.print(table)
#endregion

#region gps_to_decimal
def dms_to_decimal(coords, ref):
    degrees = float(coords[0])
    minutes = float(coords[1])
    seconds = float(coords[2])

    decimal = degrees + (minutes / 60) + (seconds / 3600)

    if ref in ("S", "W"):
        decimal = -decimal

    return decimal
#endregion

#region gps_information
def gps_information(path):
    img = Image.open(path)
    exif = img.getexif()

    try:
        gps_info = exif.get_ifd(34853)
    except AttributeError:
        gps_info = None

    if not gps_info:
        console.print("[yellow]\nGPS information not available.\n[/yellow]")
        return

    lat = gps_info.get(2)
    lat_ref = gps_info.get(1)

    lon = gps_info.get(4)
    lon_ref = gps_info.get(3)

    if not (lat and lon and lat_ref and lon_ref):
        console.print("[yellow]\nGPS coordinates not available.[/yellow]")
        return

    def format_dms(coords, ref):
        d = float(coords[0])
        m = float(coords[1])
        s = float(coords[2])
        return f'{int(d)}°{int(m)}\'{s:.2f}"{ref}'

    decimal_lat = dms_to_decimal(lat, lat_ref)
    decimal_lon = dms_to_decimal(lon, lon_ref)

    maps_url = f"https://www.google.com/maps?q={decimal_lat:.6f},{decimal_lon:.6f}"

    table = Table(title="GPS Information")
    table.border_style = "cyan"
    table.add_column("Property")
    table.add_column("Value")

    table.add_row("Latitude (DMS)", format_dms(lat, lat_ref))
    table.add_row("Longitude (DMS)", format_dms(lon, lon_ref))
    table.add_row("Latitude", f"{decimal_lat:.6f}")
    table.add_row("Longitude", f"{decimal_lon:.6f}")
    table.add_row("Google Maps", f"[link={maps_url}]{maps_url}[/link]")

    console.print(table)

#endregion

#region error_level_analysis
def error_level_analysis(path, quality=95, multiplier=15):
    """Görsel üzerinde oynama yapılıp yapılmadığını test eder ve raporlar."""
    
    # Geçici dosya adı
    tmp_file = "ela_tmp.jpg"
    
    # Orijinal görseli aç
    original = Image.open(path).convert("RGB")
    
    # Görseli %95 kalitede geçici olarak kaydet ve geri aç
    original.save(tmp_file, "JPEG", quality=quality)
    temporary = Image.open(tmp_file)
    
    # İki görsel arasındaki farkı hesapla
    from PIL import ImageChops
    diff = ImageChops.difference(original, temporary)
    
    # Farkı daha görünür kılmak için kontrastı artır (extrema analizi)
    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    
    # Parlaklığı çarpan (multiplier) ile artırarak analiz görselini oluştur
    scale = 255.0 / max_diff
    ela_image = ImageEnhance = diff.point(lambda p: p * multiplier)
    
    # Analiz sonucunu yeni bir dosya olarak kaydet
    output_filename = f"ela_{os.path.basename(path)}"
    ela_image.save(output_filename)
    
    # Geçici dosyayı temizle
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
        
    # Ekrana şık bir tablo bastır
    table = Table(title="(ELA) Error Level Analysis")
    table.add_column("Status")
    table.add_column("Result / Output Path")
    table.add_row("Success", f"[bold green]Analyzed successfully.[/bold green]")
    table.add_row("Saved Image", f"[yellow]{output_filename}[/yellow]")
    table.border_style = "cyan"
    console.print(table)
    console.print("[italic cyan]Tip: Open the saved ELA image. High brightness differences in specific areas indicate manipulation.[/italic cyan]")

#endregion

if len(sys.argv)!=2:
    console.print("[red]Usage:[/red]")
    console.print("python photo_forensics.py image.jpg")
    console.print("python photo_forensics.py 'C:\\path\\to\\image.jpg'")
    sys.exit(1)

image = sys.argv[1]
if not image.lower().endswith(SUPPORTED):
    console.print("[red]Unsupported image format.[/red]")
    sys.exit(1)

if not os.path.isfile(image):
    console.print("[bold red]Error:[/bold red] File not found!")
    console.print(f"[yellow]{os.path.abspath(image)}[/yellow]")
    sys.exit(1)

try:
    console.print("[bold cyan]\nANALYSIS STARTED[/bold cyan]")
    time.sleep(1)

    file_information(image)
    camera_information(image)
    exif_information(image)
    sha256(image)

    try:
        gps_information(image)
    except Exception as e:
        console.print(f"\n[bold red]GPS information is Not Available:[/bold red] [italic]{e}[/italic]")
        
    try:
        error_level_analysis(image)
    except Exception as e:
        console.print(f"\n[bold red]ELA Analysis Failed:[/bold red] [italic]{e}[/italic]")

    time.sleep(1)
    console.print("[bold cyan]\nANALYSIS COMPLETE[/bold cyan]")

except Exception as e:
    console.print(f"[bold red]Error:[/bold red] {e}")
    sys.exit(1)