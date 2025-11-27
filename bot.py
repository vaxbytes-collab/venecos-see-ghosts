import discord
from discord.ext import commands
from discord import app_commands
import json
from keep_alive import keep_alive

TOKEN = "TU_TOKEN_AQUI"  # Reemplaza con tu token real

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Cargar datos
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {
        "jugadores": {},   # {user_id: numero}
        "guardias": {},
        "frontman": None
    }

# Guardar datos
def save_data():
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

# Número libre para jugadores normales
def siguiente_numero_jugador():
    for n in range(2, 121):  # Cambio a 120 jugadores
        if str(n) not in data["jugadores"].values():
            return n
    return None

# --- Slash Commands ---

@tree.command(name="join", description="Únete a los Veneco Games")
async def join(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if interaction.user.bot:
        await interaction.response.send_message("Bots no pueden unirse 😎", ephemeral=True)
        return
    if user_id in data["jugadores"]:
        await interaction.response.send_message(f"Ya tienes el número {data['jugadores'][user_id]}", ephemeral=True)
        return
    numero = siguiente_numero_jugador()
    if numero is None:
        await interaction.response.send_message("Todos los números están ocupados!", ephemeral=True)
        return
    data["jugadores"][user_id] = str(numero)
    await interaction.user.edit(nick=f"[{numero:03}] {interaction.user.name}")
    save_data()
    await interaction.response.send_message(f"{interaction.user.mention} te has unido con el número {numero}!")

@tree.command(name="guardia", description="Asignar número de guardia a un jugador")
@app_commands.describe(user="Jugador a asignar", numero="Número de guardia 1-23")
async def guardia(interaction: discord.Interaction, user: discord.User, numero: int):
    if numero < 1 or numero > 23:
        await interaction.response.send_message("Número de guardia inválido (1-23)", ephemeral=True)
        return
    data["guardias"][str(user.id)] = str(numero)
    await user.edit(nick=f"[G-{numero:02}] {user.name}")
    save_data()
    await interaction.response.send_message(f"{user.mention} ahora es guardia número {numero}!")

@tree.command(name="frontman", description="Asigna al Frontman")
@app_commands.describe(user="Usuario que será el Frontman")
async def frontman(interaction: discord.Interaction, user: discord.User):
    if data["frontman"] is not None:
        await interaction.response.send_message("Ya hay un Frontman!", ephemeral=True)
        return
    data["frontman"] = str(user.id)
    await user.edit(nick=f"[001] {user.name}")
    save_data()
    await interaction.response.send_message(f"{user.mention} es el Frontman!")

@tree.command(name="reset", description="Quitar número a un jugador")
@app_commands.describe(user="Jugador a resetear")
async def reset(interaction: discord.Interaction, user: discord.User):
    uid = str(user.id)
    if uid in data["jugadores"]:
        del data["jugadores"][uid]
        await user.edit(nick=user.name)
        save_data()
        await interaction.response.send_message(f"Número de {user.mention} removido!")
    elif uid in data["guardias"]:
        del data["guardias"][uid]
        await user.edit(nick=user.name)
        save_data()
        await interaction.response.send_message(f"Guardia {user.mention} removido!")
    elif data["frontman"] == uid:
        data["frontman"] = None
        await user.edit(nick=user.name)
        save_data()
        await interaction.response.send_message(f"Frontman {user.mention} removido!")
    else:
        await interaction.response.send_message(f"{user.mention} no tiene número asignado.", ephemeral=True)

# --- Eventos ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await tree.sync()

# --- Keep alive ---
keep_alive()

# --- Run bot ---
bot.run(TOKEN)
