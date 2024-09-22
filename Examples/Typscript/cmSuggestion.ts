import { Client, Message } from 'discord.js'
import { SuggestionData } from "@prisma/client";
import { Suggestion } from './cmInterfaces';
import * as Utils from './cmUtils'
import * as MsgReply from './cmreplyFilters'
import * as Embeds from './cmEmbeds'
import * as DB from './cmDb'

// NEED TO ADD FUNCTION TO CHECK FOR DM RESPONSES FROM USER

export async function suggestionAdd(message: Message) {
    try {
        await message.channel.send(`Would you like to make a new Suggestion?`)
        const suggestReply = await MsgReply.replyGetConfirm(message)
        if (!suggestReply) { return }
        await message.channel.send(`Let me grab my Pen and Message You directly!`)
        await Utils.seconds_Delay(2)
        await message.author.send(`What would you like to Title the suggestion?`)
        const titleReply = await MsgReply.replyDMGetInfoShort(message)
        if (!titleReply) { return }
        await message.author.send(`What would you like to Suggest?`)
        const bodyReply = await MsgReply.replyDMGetInfoLong(message)
        if (!bodyReply) { return }
        await message.author.send(`Is this Correct?`)
        const date = new Date()
        const suggestionObj: Suggestion = {
            title: titleReply,
            body: bodyReply,
            date: date,
        }
        const suggestEmbed = await Embeds.createSuggest(suggestionObj)
        await message.author.send({ embeds: [suggestEmbed] })
        const confreply = await MsgReply.replyDMGetConfirm(message)
        if (!confreply) { return }
        await message.author.send(`Saving Suggestion and Reporting to Admins`)
        try {
            await DB.suggestAdd(suggestionObj)
        } catch (error) {
            console.log(`Error in Suggestion Submission: ${error}`)
        }
        await message.author.send(`Suggestion Submitted Successfully - Thank You!`)
    } catch (error) {
        console.error(`Error in Func | suggestionAdd |: ${error}`)
        throw error
    }
}

export async function suggestionList(client: Client, message: Message) {
    try {
        const botControlChannel = Utils.textChannelsList['bot-control-room']
        const suggestionsList = await DB.suggestGrabAll()
        if (!suggestionsList) {
            await botControlChannel.send(`There are no Suggestions to List`)
            return
        }
        let count = 1
        let totalCount = suggestionsList.length
        for (const suggestion of suggestionsList) {
            let suggestionEmbed = await Embeds.createSuggest(suggestion)
            botControlChannel.send({ embeds: [suggestionEmbed] })
            count++
            if (count % 4 === 0) {
                await botControlChannel.send(`Would you like to view more?`)
                let continueReply = await MsgReply.replyGetConfirm(message)
                if (!continueReply) { break }
            }
            if (count === totalCount) {
                await Utils.seconds_Delay(2)
                await message.channel.send(`Would you like to delete any of the reviewed Suggestions?`)
                const deleteReply = await MsgReply.replyGetConfirm(message)
                if (!deleteReply) {
                    await message.channel.send(`Let me know if there's anything else you need`)
                } else {
                    await message.channel.send(`Please enter the ID of the Suggestion to be deleted`)
                    const selectedSuggestion = await MsgReply.replyGetNumber(message, Array.from({ length: totalCount }, (_, i) => (i + 1).toString()))
                    if (!selectedSuggestion) { return }
                    await suggestionDelete(client, message, selectedSuggestion)
                }
            }
        }
    } catch (error) {
        console.error(`Error in Func | suggestionList |: ${error}`)
        throw error
    }
}

export async function suggestionDelete(client: Client, message: Message, selectedId: string) {
    try {
        const selectedSuggestion = await DB.suggestGrabById(selectedId)
        if (!selectedSuggestion) {
            await message.channel.send(`Error Loading Suggestion - Please try again`)
            return
        }
        await message.channel.send(`Is this correct to Delete?`)
        const selectedSuggestionEmbed = await Embeds.createSuggest(selectedSuggestion)
        await message.channel.send({ embeds: [selectedSuggestionEmbed] })
        const confdelreply = await MsgReply.replyGetConfirm(message)
        if (!confdelreply) { return }
        await DB.suggestDelete(selectedId)
        await message.channel.send(`Suggestion Deleted - Let me know if there's anything else you need.`)
    } catch (error) {
        console.error(`Error in Func | suggestionDelete |: ${error}`)
        throw error
    }
}
