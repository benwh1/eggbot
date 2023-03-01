import random
import time
from formatting import time as time_format
from discord.ext import tasks
from database import db

class RandomGame:
    def __init__(self, bot, channel_ids, game_id, message, response, freq):
        self.bot = bot
        self.channels = [bot.get_channel(c) for c in channel_ids]
        self.game_id = game_id
        self.message = message
        self.response = response
        self.freq = freq

        self.db_path = str(self.channels[0].guild.id) + f"/random_game/{game_id}/"
        self.running = False

        bot.add_listener(self.on_message)

        # initialize db keys
        if self.db_path + "scores" not in db:
            db[self.db_path + "scores"] = {}
        if self.db_path + "rounds" not in db:
            db[self.db_path + "rounds"] = {}
        if self.db_path + "round_number" not in db:
            # -1 so that the first round is round 0
            db[self.db_path + "round_number"] = -1

        # if there's already a round running and the bot was restarted for some reason, just delete it
        for x in db.prefix(self.db_path + "current"):
            del db[x]

    def scores(self):
        # sort scores in descending order
        s = db[self.db_path + "scores"]
        s = dict(sorted(s.items(), key=lambda x: -x[1]))
        return s

    def start(self):
        self.loop.start()

    async def run(self):
        self.running = True

        timestamp = time.time()

        channel = random.choice(self.channels)
        message = await channel.send(self.message)

        db[self.db_path + "current/message_id"] = message.id
        db[self.db_path + "current/channel_id"] = message.channel.id
        db[self.db_path + "current/timestamp"] = timestamp

    async def finish(self, winner_message, winner_timestamp):
        db[self.db_path + "round_number"] += 1

        round_number = db[self.db_path + "round_number"]
        message_id = db[self.db_path + "current/message_id"]
        channel_id = db[self.db_path + "current/channel_id"]
        timestamp = db[self.db_path + "current/timestamp"]
        winner_id = winner_message.author.id

        # store the round in the db
        round = {
            "message"          : message_id,
            "channel"          : channel_id,
            "timestamp"        : timestamp,
            "winner"           : winner_id,
            "winner_message"   : winner_message.id,
            "winner_timestamp" : winner_timestamp
        }
        rounds = db[self.db_path + "rounds"]
        rounds[round_number] = round
        db[self.db_path + "rounds"] = rounds

        # add a point to the lifetime scores
        scores = db[self.db_path + "scores"]
        if winner_id not in scores:
            scores[winner_id] = 1
        else:
            scores[winner_id] += 1
        db[self.db_path + "scores"] = scores

        del db[self.db_path + "current/message_id"]
        del db[self.db_path + "current/channel_id"]
        del db[self.db_path + "current/timestamp"]

        response_time = int(1000*(winner_timestamp - timestamp))
        msg = "You win!\nTime: " + time_format.format(response_time)
        if round_number > 0:
            last_round = rounds[round_number-1]
            time_since_last = int(timestamp - last_round["timestamp"])
            msg += f"\nTime since last rare {self.game_id}: " + time_format.format_long(time_since_last)

        await winner_message.reply(msg)

        self.running = False

    async def on_message(self, message):
        if message.author.bot:
            return

        if not self.running:
            return

        # get the timestamp now so we don't include extra time used by the bot
        timestamp = time.time()

        id = db[self.db_path + "current/channel_id"]
        if message.channel.id == id:
            if message.content.lower() == self.response:
                await self.finish(message, timestamp)

    @tasks.loop(seconds=1)
    async def loop(self):
        if self.running:
            return

        n = random.randint(1, self.freq)
        if n == 1:
            await self.run()
