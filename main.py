import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# Validaciones de permisos y roles
async def puede_cambiar_apodo(bot_member, target_member):
	guild = target_member.guild

	if target_member == guild.owner:
		return False, "❌ No puedo cambiar el apodo del dueño del servidor. Discord no lo permite."

	if not bot_member.guild_permissions.manage_nicknames:
		return False, "❌ No tengo el permiso `Manage Nicknames` para cambiar apodos."

	if bot_member.top_role <= target_member.top_role:
		return False, "⚠️ Mi rol no es suficientemente alto para cambiar tu apodo."

	return True, None


# Modal (formulario)
class AliasModal(Modal):

	def __init__(self, user):
		super().__init__(title="Formulario de Alias")
		self.user = user

		self.nombre = TextInput(label="Nombre", placeholder="Escribe tu nombre")
		self.apellido = TextInput(label="Apellido",
		                          placeholder="Escribe tu apellido")

		self.add_item(self.nombre)
		self.add_item(self.apellido)

	async def on_submit(self, interaction: discord.Interaction):
		nombre = self.nombre.value.strip()
		apellido = self.apellido.value.strip()

		if not nombre:
			await interaction.response.send_message(
			    "⚠️ El nombre no puede estar vacío.", ephemeral=True)
			return

		if not apellido:
			await interaction.response.send_message(
			    "⚠️ El apellido no puede estar vacío.", ephemeral=True)
			return

		nuevo_alias = f"{nombre} {apellido}"

		# Mostrar botones para confirmar o reintentar
		view = ConfirmAliasView(self.user, nuevo_alias)
		embed = discord.Embed(
		    title="Confirmar alias",
		    description=f"¿Querés usar el alias:\n**{nuevo_alias}**?",
		    color=discord.Color.blue(),
		)

		await interaction.response.send_message(embed=embed,
		                                        view=view,
		                                        ephemeral=True)


# Botones para confirmar o cancelar alias
class ConfirmAliasView(View):

	def __init__(self, user, alias):
		super().__init__(timeout=60)
		self.user = user
		self.alias = alias

	@discord.ui.button(label="✅ Sí", style=discord.ButtonStyle.success)
	async def confirmar(self, interaction: discord.Interaction, button: Button):
		try:
			await self.user.edit(nick=self.alias)
			await interaction.response.send_message(
			    f"✅ Tu alias ha sido cambiado a `{self.alias}`", ephemeral=True)
		except discord.Forbidden:
			await interaction.response.send_message(
			    "❌ No tengo permisos para cambiar tu alias.", ephemeral=True)

		self.stop()

	@discord.ui.button(label="🔁 Reintentar", style=discord.ButtonStyle.secondary)
	async def reintentar(self, interaction: discord.Interaction, button: Button):
		modal = AliasModal(self.user)
		await interaction.response.send_modal(modal)
		self.stop()

	@discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger)
	async def cancelar(self, interaction: discord.Interaction, button: Button):
		await interaction.response.send_message("❌ Operación cancelada.",
		                                        ephemeral=True)
		self.stop()


# Vista con botón para abrir el modal
class AliasStartView(View):

	def __init__(self, user):
		super().__init__(timeout=60)
		self.user = user

	@discord.ui.button(label="📝 Ingresar nombre y apellido",
	                   style=discord.ButtonStyle.primary)
	async def abrir_modal(self, interaction: discord.Interaction, button: Button):
		if interaction.user != self.user:
			await interaction.response.send_message("⛔ Solo vos podés usar este botón.",
			                                        ephemeral=True)
			return

		modal = AliasModal(self.user)
		await interaction.response.send_modal(modal)


@bot.command()
async def alias(ctx):
	user = ctx.author
	bot_member = ctx.guild.me

	puede, error = await puede_cambiar_apodo(bot_member, user)
	if not puede:
		await ctx.send(error)
		return

	# Abrir directamente el formulario
	modal = AliasModal(user)
	await ctx.send("📝 Abriendo formulario para cambiar tu alias...",
	               delete_after=5)
	await ctx.send_modal(modal)


# Mantener activo el bot en Replit
keep_alive()

token = os.getenv("TOKEN")
if not token:
	raise ValueError("❌ TOKEN no encontrado en .env")
bot.run(token)
