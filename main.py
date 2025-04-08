import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

# Cargar variables del .env
load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


# Verifica si el bot puede cambiar el apodo del usuario
async def puede_cambiar_apodo(bot_member, target_member):
	guild = target_member.guild

	# ⚠️ Discord no permite cambiar el apodo del dueño del servidor
	if target_member == guild.owner:
		return False, "❌ No puedo cambiar el apodo del dueño del servidor. Discord no lo permite."

	# ¿El bot tiene el permiso Manage Nicknames?
	if not bot_member.guild_permissions.manage_nicknames:
		return False, "❌ No tengo el permiso `Manage Nicknames` para cambiar apodos."

	# ¿Está el rol del bot por encima del del usuario?
	if bot_member.top_role <= target_member.top_role:
		return False, "⚠️ Mi rol no es suficientemente alto para cambiar tu apodo."

	return True, None


@bot.command()
async def alias(ctx):
	user = ctx.author
	channel = ctx.channel
	guild = ctx.guild
	bot_member = guild.me

	def check(m):
		return m.author == user and m.channel == channel

	puede, error = await puede_cambiar_apodo(bot_member, user)
	if not puede:
		await ctx.send(error)
		return

	intentos = 0
	max_intentos = 3

	while intentos < max_intentos:
		try:
			await ctx.send("👋 Hola, ¿cuál es tu **nombre**?")
			nombre = await bot.wait_for("message", check=check, timeout=60)

			await ctx.send("¿Y tu **apellido**?")
			apellido = await bot.wait_for("message", check=check, timeout=60)

			nuevo_alias = f"{nombre.content} {apellido.content}"

			await ctx.send(
			    f"❓ ¿Querés usar el alias **{nuevo_alias}**? Responde con `S` para sí o `N` para no."
			)

			confirmacion = await bot.wait_for("message",
			                                  check=check,
			                                  timeout=30)
			respuesta = confirmacion.content.strip().lower()

			if respuesta == "s":
				await user.edit(nick=nuevo_alias)
				await ctx.send(f"✅ ¡Listo! Tu nuevo alias es: `{nuevo_alias}`")
				break
			elif respuesta == "n":
				intentos += 1
				await ctx.send(
				    f"🔁 Ok, intentemos de nuevo. Intento {intentos}/{max_intentos}.\n"
				)
			else:
				intentos += 1
				await ctx.send(
				    f"❌ Respuesta inválida. Usá `S` o `N`. Intento {intentos}/{max_intentos}.\n"
				)

		except asyncio.TimeoutError:
			await ctx.send(
			    "⏰ Se acabó el tiempo. Intenta otra vez cuando quieras.")
			break
		except discord.Forbidden:
			await ctx.send(
			    "❌ No tengo permisos suficientes para cambiar tu apodo.")
			break
		except Exception as e:
			await ctx.send(f"⚠️ Ocurrió un error inesperado: {e}")
			break

	if intentos >= max_intentos:
		await ctx.send("🚫 Demasiados intentos fallidos. Intentalo más tarde.")


# Mantiene vivo el bot en Replit
keep_alive()

# Ejecutar el bot
token = os.getenv("TOKEN")
if not token:
	raise ValueError("❌ TOKEN no encontrado. Por favor, notifique a un ADMIN")
bot.run(token)
