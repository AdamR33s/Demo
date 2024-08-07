import { GuildMember } from 'discord.js';
import * as Interfaces from './cmInterfaces'
import * as cmData from './cmData'
import { PrismaClient } from '@prisma/client';
import { AdminType } from '@prisma/client';

const prisma = new PrismaClient();

// SYSTEM FUNCTIONS
export async function sysControlsCreateAll() {
    try {
        for(const controller of Object.values(cmData.sysControlData)) {
            const createData = await prisma.systemControl.create({
                data: {
                    name: controller.name,
                    bool: controller.bool,
                    int: controller.int,
                    str: controller.str,
                    dt: controller.dt,
                    list: controller.list
                }
            })
            if(!createData) {
                throw new Error(`Unable to Create System Control Data`)
            }
        }
    } catch (error) {
        console.error(`Error in Func | sysControlCreateAll |: ${error}`)
        throw error
    }
}

export async function sysControlsGrabByName(controlName: string) {
    try {
        const sysControl = await prisma.systemControl.findUnique({
            where: { name: controlName }
        })
        if(sysControl) {
            return sysControl
        } else {
            throw new Error(`Unable to Load System Control ${controlName}`)
        }
    } catch (error) {
    console.error(`Error in Func | sysControlGrabByName |: ${error}`)
    throw error
    }
}

export async function sysControlsUpdate(sysControl: Interfaces.systemControl) {
    try {
        const updateData = await prisma.systemControl.update({
            where: { name: sysControl.name },
            data: {
                bool: sysControl.bool,
                int: sysControl.int,
                str: sysControl.str,
                dt: sysControl.dt,
                list: sysControl.list
            }
        })
        if(!updateData) {
            throw new Error(`Unable to update System Control Data`)
        }
    } catch (error) {
        console.error(`Error in Func | sysControlsUpdate |: ${error}`)
        throw error
    }
}

export async function sysControlsDeleteAll() {
    try {
        const sysControlDeleteData = await prisma.systemControl.deleteMany({})
    if(!sysControlDeleteData) {
        throw new Error(`Unable to Delete System Control Data`)
        }
    } catch (error) {
        console.error(`Error in Func | sysControlsDeleteAll |: ${error}`)
        throw error
    }
}

// USER FUNCTIONS
export async function userAdd(member: GuildMember, adminType?: AdminType ) {
    try {
        const newUser = await prisma.users.create({
                data: {
                    discordId: member.id,
                    userName: member.user.username,
                    displayName: member.displayName,
                    survRank: "Community Survivor",
                    adminRank: adminType
                }
            })
        if(!newUser) {
            throw new Error(`New User couldn't be saved to the DB`)
        }
    } catch (error) {
    console.error(`Error in Func | userAdd |: ${error}`)
    throw error
    }
}

export async function userGrabById(memberId: string) {
    try {
        const user = await prisma.users.findUnique({
        where: { discordId: memberId } 
        });
        if(user) {
            return user
        } else {
            console.log(`Unable to find User by ID`)
            return null
        }
    } catch (error) {
        console.error(`Error in Func | userGrabById |: ${error}`)
        throw error
    }
}

//NEWS FUNCTIONS
export async function newsAdd(news: Interfaces.News) {
    try {
        const newNews = await prisma.news.create({
            data: {
                title: news.title,
                body: news.body,
                image: news.image,
                link: news.link,
                date: news.date,
                sent: 0
            }
        })
        if(!newNews) {
            throw new Error(`New News couldn't be saved to the DB`)
        }
    } catch (error) {
        console.error(`Error in Func | newsAdd |: ${error}`)
        throw error
    }
}

export async function newsGrabById(id: string) {
    try {
        const news = await prisma.news.findUnique({
            where: { id: Number(id) }
        })
        if(news) {
            return news
        } else {
            console.log("Unable to find News by ID")
            return null
        }
    } catch (error) {
        console.error(`Error in Func | newsGrabById |: ${error}`)
        throw error
    }
}

export async function newsGrabAll() {
    try {
        const newsRows = await prisma.news.findMany({
            orderBy: { date: 'asc'}
        })
        if(newsRows && newsRows.length > 0) {
            return newsRows
        } else {
            console.log(`No News to Load`)
            return null
        }
    } catch (error) {
        console.error(`Error in Func | newsGrabAll |: ${error}`)
        throw error
    }
}

export async function newsGrabNext() {
    try {
        const newsRows = await newsGrabAll()
        if(newsRows) {
            return newsRows[0]
        } else {
            return null
        }
    } catch (error) {
        console.error(`Error in Func | newsGrabNext |: ${error}`)
        throw error
    }
}

export async function newsUpdateSent(news: Interfaces.News) {
    try {
        const updateData = await prisma.news.update({
            where: { id: news.id },
            data: { sent: {increment: 1} }
        })
        if(!updateData) {
            throw new Error(`Error Updating News Sent Count`)
        }
    } catch (error) {
        console.error(`Error in Func | newsUpdateSent |: ${error}`)
        throw error
    }
}

export async function newsDelete(newsId: string) {
    try {
        const removeNews = await prisma.news.delete({
            where: { id: Number(newsId) }
        })
        if(!removeNews) {
            throw new Error(`Unable to remove News Item`)
        }
    } catch (error) {
        console.error(`Error in Func | newsRemove |: ${error}`)
        throw error
    }
}

// ADVERT FUNCTIONS
export async function advertsCreateAll() {
    try {
        for(const advert of Object.values(cmData.advertData)) {
            const createData = await prisma.adverts.create({
                data: {
                    title: advert.title,
                    body: advert.body,
                    mentionChannelId: advert.mentionChannelId,
                    lastSent: advert.lastSent
                }
            })
            if(!createData) {
                throw new Error(`Error Creating Adverts from advertData`)
            }
        }   
    } catch (error) {
        console.error(`Error in Func | advertsCreateAll |: ${error}`)
        throw error
    }
}

export async function advertsGrabAll() {   
    try {
        const advertRows = await prisma.adverts.findMany({
            orderBy: { lastSent: 'asc' }
        });
        if(advertRows && advertRows.length > 0) {
            return advertRows
        } else {
            console.log(`No Adverts to Load`)
            return null
        }
    } catch (error) {
        console.error(`Error in Func | advertsGrabAll |: ${error}`)
        throw error
    }
}

export async function advertsUpdateSent(selectedAdvert: Interfaces.Advert, currentTime: Date) {
    try {        
        const updateAdvert = await prisma.adverts.update({
        where: { id: selectedAdvert.id },
        data: { lastSent: currentTime }
        });
        if(!updateAdvert) {
            throw new Error("Advert Sent Data couldn't be updated.")
        }
    } catch (error) {
        console.error(`Error in Func | advertsUpdateSent |: ${error}`)
        throw error
    }
}

export async function advertsDeleteAll() {
    try { 
        const deleteData = await prisma.adverts.deleteMany({})
        if(!deleteData) {
            throw new Error("Adverts Data couldn't be Deleted")
        }
    } catch (error) {
        console.error(`Error in Func | advertsDeleteAll |: ${error}`)
        throw error
    }
}

// SUGGESTION FUNCTIONS
export async function suggestAdd(usertitle: string, userbody: string, currentDate: Date ) {
    try {
        const newSuggestion = await prisma.suggestion.create({
            data: {
                title: usertitle,
                body: userbody,
                date: currentDate
            }
        })
    if(!newSuggestion) {
        throw new Error(`Error saving new Suggestion Data`)
    }
    } catch (error) {
        console.error(`Error in Func | suggestAdd |: ${error}`)
        throw error
    }
}

export async function suggestGrabById(id: string) {
    try {
        const suggestion = await prisma.suggestion.findUnique({
            where: { 
                id: Number(id)
            }
        })
        if(suggestion) {
            return suggestion
        } else {
            console.log(`Unable to find Suggestion`)
            return null
        }
    } catch (error) {
        console.error(`Error in Func | suggestGrabById |: ${error}`)
        throw error
    }
}

export async function suggestGrabAll() {
    try {
        const suggestionRows = await prisma.suggestion.findMany({
            orderBy: { date: 'asc' }
        });
        if(suggestionRows) {
            return suggestionRows
        } else {
            console.log(`No Suggestions to Load`)
            return null
        }
    } catch (error) {
        console.error(`Error in Func | suggestGrabAll |: ${error}`)
        throw error
    }
}

export async function suggestDelete(id: string) {
    try {
        const deleteSuggestion = await prisma.suggestion.delete({
            where: {
                id: Number(id)
            }
        })
        if(!deleteSuggestion) {
            throw new Error(`Suggestion couldn't be Deleted`)
        }
    } catch (error) {
        console.error(`Error in Func | suggestDeleteById |: ${error}`)
    }
}