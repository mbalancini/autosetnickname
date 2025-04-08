import discord
from discord.ext import commands
import asyncio
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
async def alias(ctx):
	user = ctx.author
	channel = ctx.channel
	guild = ctx.guild

	def check(m):
		return m.author == user and m.channel == channel

	bot_member = guild.me

	# Verificación de permisos antes de comenzar
	if not guild.me.guild_permissions.manage_nicknames:
		await ctx.send(
			"❌ No tengo el permiso `Administrar apodos` en este servidor.")
		return

	# Verifica si el bot puede cambiar el apodo del usuario (jerarquía de roles)
	if user.top_role >= bot_member.top_role:
		await ctx.send(
			"⚠️ No puedo cambiar tu apodo porque tu rol está por encima del mío."
		)
		return

	while True:
		try:
			await ctx.send("👋 Hola, ¿cuál es tu **nombre**?")
			nombre = await bot.wait_for("message", check=check, timeout=60)

			await ctx.send("¿Y tu **apellido**?")
			apellido = await bot.wait_for("message", check=check, timeout=60)

			nuevo_alias = f"{nombre.content} {apellido.content}"

			await ctx.send(
				f"❓¿Quieres usar el alias **{nuevo_alias}**? Responde con `S` para sí o `N` para no."
			)

			confirmacion = await bot.wait_for("message",
													check=check,
													timeout=30)
			respuesta = confirmacion.content.strip().lower()

			if respuesta == "s":
				await user.edit(nick=nuevo_alias)
				await ctx.send(f"✅ Tu nuevo alias es: `{nuevo_alias}`")
				break
			elif respuesta == "n":
				await ctx.send("🔁 Entendido, vamos a empezar de nuevo.\n")
			else:
				await ctx.send("❌ Respuesta no válida. Empecemos de nuevo.\n")

		except asyncio.TimeoutError:
			await ctx.send("⏰ Se acabó el tiempo. Intenta otra vez.")
			break
		except discord.Forbidden:
			await ctx.send("❌ No tengo permisos para cambiar tu apodo.")
			break
		except Exception as e:
			await ctx.send(f"⚠️ Ocurrió un error: {e}")
			break


# Mantiene vivo el bot (para Replit)
keep_alive()

# Corre el bot
load_dotenv()

token = os.getenv("TOKEN")
if not token:
	raise ValueError(
		"❌ No se encontró la variable de entorno 'TOKEN'. Verifica tu archivo .env"
	)

bot.run(token)
