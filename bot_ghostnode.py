
import discord
from discord.ext import commands
from discord.ui import View, Button
import os
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ A variável de ambiente 'TOKEN' não está definida!")
CODIGOS_FILE = "codigos_100k.json"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CARGO_MENSAL_ID = 1368420926248714291
CARGO_VITALICIO_ID = 1368421033283162172
STAFF_ROLE_NAME = "🎫│ticket"
TICKET_CATEGORY = "⇓━━━━━━━━  Atendimento ━━━━━━━━⇓"

class PlanoView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Plano Mensal", style=discord.ButtonStyle.primary, custom_id="plano_mensal"))
        self.add_item(Button(label="Plano Vitalício", style=discord.ButtonStyle.success, custom_id="plano_vitalicio"))
        self.add_item(Button(label="Suporte", style=discord.ButtonStyle.secondary, custom_id="suporte"))

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")
    bot.add_view(PlanoView())

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="📋 Qual o seu plano? Precisa de ajuda?",
        description="Escolha uma das opções abaixo:",
        color=discord.Color.dark_blue()
    )
    embed.set_image(url="https://i.imgur.com/oQQL8Pb.png")
    await ctx.send(embed=embed, view=PlanoView())

@bot.command()
async def validar(ctx, codigo: str):
    user = ctx.author
    if not os.path.exists(CODIGOS_FILE):
        await ctx.send("❌ Arquivo de códigos não encontrado.")
        return

    with open(CODIGOS_FILE, "r") as f:
        dados = json.load(f)

    if codigo in dados["usados"]:
        await ctx.send("❌ Este código já foi utilizado.")
        return

    if codigo in dados["mensal"]:
        role = ctx.guild.get_role(CARGO_MENSAL_ID)
        await user.add_roles(role)
        dados["mensal"].remove(codigo)
        dados["usados"].append(codigo)
        await ctx.send("✅ Código válido! Plano Mensal ativado.")
    elif codigo in dados["vitalicio"]:
        role = ctx.guild.get_role(CARGO_VITALICIO_ID)
        await user.add_roles(role)
        dados["vitalicio"].remove(codigo)
        dados["usados"].append(codigo)
        await ctx.send("✅ Código válido! Acesso Vitalício concedido.")
    else:
        await ctx.send("❌ Código inválido.")

    with open(CODIGOS_FILE, "w") as f:
        json.dump(dados, f, indent=2)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if not interaction.data: return
    custom_id = interaction.data.get("custom_id")
    guild = interaction.guild
    user = interaction.user

    if custom_id == "plano_mensal":
        await interaction.response.send_message("🔒 Use o comando ```!validar MENSAL-000000``` para ativar seu plano. Exemplo: `!validar MENSAL-183567`. Seu código foi fornecido junto ao link de pagamento.", ephemeral=True)
    elif custom_id == "plano_vitalicio":
        await interaction.response.send_message("🔒 Use o comando ```!validar VITA-000000``` para ativar seu plano. Exemplo: `!validar VITA-183567`. Seu código foi fornecido junto ao link de pagamento.", ephemeral=True)
    elif custom_id == "suporte":
        categoria = discord.utils.get(guild.categories, name=TICKET_CATEGORY)
        if not categoria:
            categoria = await guild.create_category(TICKET_CATEGORY)

        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        canal = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=categoria,
            overwrites=overwrites
        )

        await canal.send(f"📩 {user.mention}, sua solicitação de suporte foi criada. Aguarde atendimento.")
        await interaction.response.send_message(f"✅ Canal de suporte criado: {canal.mention}", ephemeral=True)

bot.run(TOKEN)
