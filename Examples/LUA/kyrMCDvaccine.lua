--NEW FILE
kyrVAC = {}

function kyrVAC.addPlayer(player)
    local pMD = player:getModData()
    pMD.kyrMCD.vaccine = true
    pMD.kyrMCD.vaccineTimer = 0
end

function kyrVAC.vaccineCheck()
    local player = getPlayer()
    local pMD = player:getModData()
    local bodyDamage = player:getBodyDamage()
    local bodyParts = bodyDamage:getBodyParts()
    if not pMD.kyrMCD.vaccine then return end
    bodyDamage:setInfected(false)
    bodyDamage:setInfectionMortalityDuration(-1)
    bodyDamage:setInfectionTime(-1)
    bodyDamage:setInfectionLevel(0)
    for i=bodyParts:size()-1, 0, -1 do
        local bodyPart = bodyParts:get(i)
        bodyPart:SetInfected(false)
    end
    pMD.kyrMCD.vaccineTimer = pMD.kyrMCD.vaccineTimer + 1
    if pMD.kyrMCD.vaccineTimer == 336 then -- 2 WEEKS
        pMD.kyrMCD.vaccine = false
        pMD.kyrMCD.vaccineTimer = 0
    end
end

return kyrVAC