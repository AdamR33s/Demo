import { Client } from 'discord.js';
import * as Utils from './cmUtils';
import * as Interfaces from './cmInterfaces';
import * as Embeds from './cmEmbeds'
import * as DB from './cmDb'
import { Interface } from 'node:readline';

export async function autoService(client: Client) {
    try {
        const advertsController = await DB.sysControlsGrabByName(`Adverts`)
        await controllerCheck(advertsController)
        if(advertsController.bool === false) { return }
        const randomAdvert = await selectRandom(client)
        await print(randomAdvert)
        advertsController.dt = new Date()
        await DB.sysControlsUpdate(advertsController)
    } catch (error) {
        console.error(`Error in Func | advertsRandomSend |: ${error}`)
        throw error
    }
}

export async function print(advert: Interfaces.Advert) {
    try {
        const advert_embed = await Embeds.createAdvert(advert);
        const chat_channel = Utils.textChannelsList[`chat`]
        await chat_channel.send({ embeds: [advert_embed] });
        await DB.advertsUpdateSent(advert, new Date())
    } catch (error) {
        console.error(`Error in Func | advertPrint |: ${error}`)
        throw error
    }
}

async function controllerCheck(advertsController: Interfaces.systemControl) {
    if(advertsController.dt) {
        if((advertsController.dt.getTime() - new Date().getTime()) > 36 * 60 * 60 * 1000 ) {
            advertsController.bool = true
        } else {
            advertsController.bool = false
        }
    } else {
        advertsController.dt === new Date()
        advertsController.bool = true
    }
    await DB.sysControlsUpdate(advertsController)
    return advertsController
}

async function selectRandom(client: Client) {
    try {
        const suitableAds = new Array
        const advertRows: Interfaces.Advert[] | null = await DB.advertsGrabAll()
        if(!advertRows) {
            await Utils.textChannelsList[`bot-control-room`].send(`No Adverts to Send`)
            return
        }
        advertRows.filter(advert => {
            if (advert.lastSent === null || advert.lastSent === undefined) {
                suitableAds.push(advert)
            } else {
                const timeDifference = new Date().getTime() - advert.lastSent.getTime();
                const hoursSinceLastSent = timeDifference / (1000 * 60 * 60);
                if(hoursSinceLastSent >= 36) {
                    suitableAds.push(advert)
                }
            }
        });
        if (suitableAds.length === 0) {
            console.log(`No suitable advert found.`);
            return;
        }
        await Utils.shuffleArray(suitableAds)
        const selectedAdvert = suitableAds.pop()
        return selectedAdvert
    } catch (error) {
        console.error(`Error in Func | advertSelectRandom |: ${error}`)
        throw error
    }
}