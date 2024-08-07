import { Client } from 'discord.js';
import * as System from './cmSystem'
import * as Utils from './cmUtils.js';
import * as Services from './cmServices.js';
import * as Members from './cmUsers.js';
import * as Logs from './cmLogs'


const client = new Client({
	intents: [
		`Guilds`,
		`GuildMessages`,
		`GuildMessageReactions`,
		`DirectMessages`,
		`MessageContent`,
		`GuildMembers`,
	],
});

client.on(`ready`, async () => {
	//
	try {
		console.log(`Running Data Checks...`)
		await System.sysBootCheck(client);
		console.log(`Loading Channel List`)
		await Utils.liveChannelList(client);
		console.log(`Loading Role List`)
		await Utils.liveRoleList(client);
		console.log(`[KYR] Community Manager Online!`);
		return;
	} catch (error) {
		console.error(":: ERROR DURRING BOOT ::", error)
		Logs.logWrite(`BOOT ERROR`, error)
		process.exit(1)
	}
});

client.on(`guildMemberAdd`, async (member) => {
	await Members.memberJoin(member)
})

client.on(`messageCreate`, async (message) => {
	await Services.message_Broker(client, message);
});

//Client Login Would go Here!
