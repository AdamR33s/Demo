using System;

public class PlayerShipStats // Setup Stats Type and Variables for Player Ship
{
    public enum PlayerShipStatType
    {
        Integrity,
        Shield,
        Fuel,
        SuperFuel,
        ElectricCharge,
    }

    public class Fuel
    {
        public string Type { get; private set; }
        public float BurnRate { get; private set; }
        public float Acceleration { get; private set; }
        public float MaxSpeed { get; private set; }
        public float Amount { get; private set; }

        public void Change(Fuels.Type fuelType)
        {
            Fuels.FuelStruct NewFuelData;
            switch (fuelType)
            {
                case Fuels.Type.Hydrazine:
                    NewFuelData = Fuels.Hydrazine;
                    break;
                case Fuels.Type.UDHM:
                    NewFuelData = Fuels.UDHM;
                    break;
                case Fuels.Type.MMH:
                    NewFuelData = Fuels.MMH;
                    break;
                case Fuels.Type.Aerozine50:
                    NewFuelData = Fuels.Aerozine50;
                    break;
                default:
                    throw new ArgumentOutOfRangeException(nameof(fuelType), fuelType, "Fuel type not found.");
            }
            Type = NewFuelData.Type;
            BurnRate = NewFuelData.BurnRate;
            Acceleration = NewFuelData.Acceleration;
            MaxSpeed = NewFuelData.MaxSpeed;
        }

        public void Add(float amount, float MaxAmount)
        {
            Amount = Math.Min(MaxAmount, Amount + amount);
        }

        public bool Burn(float delta)
        {
            if (Amount <= 0)
            {
                return false;
            }
            Amount = Math.Max(0, Amount - 1.0f * BurnRate * delta); //FUEL DEPLETION RATE IS 1UNIT/SECOND BY DEFAULT
            return true;
        }
    }

    public class SuperFuel
    {
        public string Type { get; private set; }
        public float BurnRate { get; private set; }
        public float Acceleration { get; private set; }
        public float MaxSpeed { get; private set; }
        public float Amount { get; private set; }

        public void Change(SuperFuels.Type superFuelType)
        {
            SuperFuels.SuperFuelStruct NewSuperFuelData;
            switch (superFuelType)
            {
                case SuperFuels.Type.LH2N204:
                    NewSuperFuelData = SuperFuels.LH2N204;
                    break;
                case SuperFuels.Type.LH2LOX:
                    NewSuperFuelData = SuperFuels.LH2LOX;
                    break;
                default:
                    throw new ArgumentOutOfRangeException(nameof(superFuelType), superFuelType, "SuperFuel type not found.");
            }
            Type = NewSuperFuelData.Type;
            BurnRate = NewSuperFuelData.BurnRate;
            Acceleration = NewSuperFuelData.Acceleration;
            MaxSpeed = NewSuperFuelData.MaxSpeed;
        }

        public void Add(float amount, float MaxAmount)
        {
            Amount = Math.Min(MaxAmount, Amount + amount);
        }

        public bool Burn(float delta)
        {
            if (Amount <= 0)
            {
                return false;
            }
            Amount = Math.Max(0, Amount - 1.0f * BurnRate * delta); //FUEL DEPLETION RATE IS 1UNIT/SECOND BY DEFAULT
            return true;
        }
    }

    public float Integrity { get; private set; } = 100.00f;
    public float MaxIntegrity { get; private set; } = 100.00f;
    public float Shield { get; private set; } = 100.00f;
    public float MaxShield { get; private set; } = 100.00f;
    public Fuel CurrentFuel { get; private set; } = new Fuel();
    public float MaxFuel { get; private set; } = 100.00f;
    public SuperFuel CurrentSuperFuel { get; private set; } = new SuperFuel();
    public float MaxSuperFuel { get; private set; } = 20.00f;
    public float ElectricCharge { get; private set; } = 100.00f;
    public float MaxElectricCharge { get; private set; } = 100.00f;
}