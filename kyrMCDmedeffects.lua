--NEW FILE
kyrEFF = {}

--[[ Effects Tables ]]--
local deadlyEffects = {
	["Burns"] = 10,
    ["Exhaustion"] = 15,
	["Cold"] = 25,
	["Sick"] = 25,
}

local strongEffects = {
	["Cold"] = 10,
    ["Exhaustion"] = 15,
    ["Unhappy"] = 20,
	["Sick"] = 20,
}

local mildEffects = {
	["Thirst"] = 25,
	["Hunger"] = 25,
	["Panic"] = 35,
}

local effectsTables = {deadlyEffects, strongEffects, mildEffects}
local impactTables = {'deadly', 'strong', 'mild'}

local function kyrEFF_checkTotalChance(table)
	local total_chance = 0
	for _, chance in pairs(table) do
		total_chance = total_chance + chance
	end
	return total_chance
end

local function kyrEFF_checkImpact(impactType)
    if impactType == 'deadly' then
        return ZombRand(76, 95)
    elseif impactType == 'strong' then
        return ZombRand(51, 75)
    elseif impactType == 'mild' then
        return ZombRand(26,50)
    end
end

local function kyrEFF_get_Speech(effect, stage)
    local speech = ''
    local randomSpeech = ZombRand(1,3)
    if stage == 'ONCOMING' or stage == 'HIT' then 
        speech = getText('UI_KYR_' .. effect:upper() .. '_' .. stage:upper() .. tostring(randomSpeech))
    end
    return speech
end

local function kyrEFF_saveEffects(player, selectedEffects)
    local pMD = player:getModData()
    for index, effect in ipairs(selectedEffects) do
        table.insert(pMD.kyrMCD.medEffects, effect)
    end
end

local function kyrEFF_selectRandomEffects(rolls)
    local selectedEffects = {}
    for index, rollType in ipairs(rolls) do
        local effectTable = effectsTables[index]
        for i=1, rollType do
            local total_chance = ZombRand(1, kyrEFF_checkTotalChance(effectTable))
            local impact = 0
            for effect, chance in pairs(effectTable) do
                total_chance = total_chance - chance
                if total_chance <= 0 then
                    impact = kyrEFF_checkImpact(impactTables[index])
                    table.insert(selectedEffects, effect .. ":" ..  impact)
                    break
                end
            end
        end
    end
    return selectedEffects
end

local function kyrEFF_Get_Random_BodyPart(player)
	local body_parts_list = {}
	local bodyparts = player:getBodyDamage():getBodyParts()
	for i=0,bodyparts:size()-1 do
		table.insert(body_parts_list, bodyparts:get(i))
	end
	local selected_bodypart = body_parts_list[ZombRand(#body_parts_list)]
	return selected_bodypart
end

function kyrEFF.applyMedEffects()
    local player = getPlayer()
    local pMD = player:getModData()
    local mEffects = pMD.kyrMCD.medEffects
    if not mEffects then return end
    if #mEffects == 0 then return end
    local mEffectsT = pMD.kyrMCD.medEffectsTimer
    local mEffectsIT = pMD.kyrMCD.medImpactTimer
    local bodyDamage = player:getBodyDamage()
	local stats = player:getStats()
    local effect, impact = string.match(mEffects[1], "(%w+):(%d+)")
    if mEffectsIT == 0 then
        mEffectsIT = ZombRand(3, 5) -- TEST CHANGES RETURN TO 144/6Days, 215/9Days - 1 Hour for Reset
    end
    if mEffectsT + 1 == mEffectsIT then -- TEST CHANGES RETURN TO '- 24 == 0'
		player:Say(kyrEFF_get_Speech(effect, 'ONCOMING'))
	end
    if mEffectsT == mEffectsIT then
        local randomSpeech = ZombRand(1, 3)
		impact = tonumber(impact)
        if effect == "Burns" then
			local bodyPart = kyrEFF_Get_Random_BodyPart(player)
			bodyDamage:getBodyPart(BodyPartType[bodyPart]):setBurned()
		elseif effect == "Cold" then
			bodyDamage:setHasACold(true)
			bodyDamage:setColdStrength(bodyDamage:getColdStrength() + impact)
			if bodyDamage:getColdStrength() > 100 then
				bodyDamage:setColdStrength(95)
			end
        elseif effect == "Sick" then
			bodyDamage:setFoodSicknessLevel(bodyDamage:getFoodSicknessLevel() + impact)
			if bodyDamage:getFoodSicknessLevel() > 100 then
				bodyDamage:setFoodSicknessLevel(95)
			end
		elseif effect == "Exhaustion" then
			if stats:getEndurance() > 0 then
                stats:setEndurance(0)
            end
		elseif effect == "Hunger" then
			stats:setHunger(stats:getHunger() + (impact/100))
			if stats:getHunger() > 1 then
				stats:setHunger(0.95)
			end
		elseif effect == "Thirst" then
			stats:setThirst(stats:getThirst() + (impact/100))
			if stats:getThirst() > 1 then
				stats:setThirst(0.90)
			end
		elseif effect == "Panic" then
			stats:setPanic(stats:getPanic() + impact)
			if stats:getPanic() > 100 then
				stats:setPanic(100)
			end
		elseif effect == "Unhappy" then
			bodyDamage:setUnhappynessLevel(bodyDamage:getUnhappynessLevel() + impact)
			if bodyDamage:getUnhappynessLevel() > 100 then
				bodyDamage:setUnhappynessLevel(100)
			end
		end
        player:Say(kyrEFF_get_Speech(effect, 'HIT'))
        table.remove(mEffects, 1)
    end
    mEffectsT = mEffectsT + 1
    if mEffectsT == 6 then -- TEST CHANGES RETURN TO 9 DAYS / 216 HOURS, RESET SYSTEM TO 0
        mEffectsT = 0
        mEffectsIT = 0
    end
    pMD.kyrMCD.medEffects = mEffects
    pMD.kyrMCD.medEffectsTimer = mEffectsT
    pMD.kyrMCD.medImpactTimer = mEffectsIT
end

function kyrEFF.randomMedEffects(rolls)
    local player = getPlayer()
    local pMD = player:getModData()
    local mEffects = pMD.kyrMCD.medEffects
    if #mEffects >= 26 then return end
    local randomEffects = kyrEFF_selectRandomEffects(rolls)
    kyrEFF_saveEffects(player, randomEffects)
end

return kyrEFF