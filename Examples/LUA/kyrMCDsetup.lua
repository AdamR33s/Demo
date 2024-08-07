--NEW FILE
local kyrVAC = require 'kyrMCDvaccine'
local kyrEFF = require 'kyrMCDmedeffects'

--[[ MCD Setup ]]--
local function kyrMCD_Setup()
    -- pMD.kyrMCD = {} -- TEST CHANGES - Uncomment to reset all MCD Data
	local player = getPlayer()
	local pMD = player:getModData()
    -- Med Effects Setup
	pMD.kyrMCD = pMD.kyrMCD or {}
	pMD.kyrMCD.medEffects = pMD.kyrMCD.medEffects or {}
    pMD.kyrMCD.medEffectsTimer = pMD.kyrMCD.medEffectsTimer or 1
    pMD.kyrMCD.medImpactTimer = pMD.kyrMCD.medImpactTimer or 0
    -- Vaccine Setup
    pMD.kyrMCD.vaccine = pMD.kyrMCD.vaccine or false
    pMD.kyrMCD.vaccineTimer = pMD.kyrMCD.vaccineTimer or 0
end

--[[ EVENTS Setup ]]--
if not isServer() then
    Events.OnGameStart.Add(kyrMCD_Setup)
    Events.EveryHours.Add(kyrVAC.vaccineCheck)
    Events.EveryHours.Add(kyrEFF.applyMedEffects)
end