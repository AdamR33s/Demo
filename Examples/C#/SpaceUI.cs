using System;
using System.Collections.Generic;
using Godot;

public partial class SpaceUI : CanvasLayer
{
    private PlayerShip playerShip; // Martian and Related Attributes
    private PlayerEngines playerEngines;
    private Timer updateUITimer;
    private Label statsUIHealth;
    private TextureProgressBar statsUIHealthBar;
    private Label statsUIShield;
    private TextureProgressBar statsUIShieldBar;
    private Label fuelUIFuel;
    private TextureProgressBar fuelUIFuelBar;
    private Label fuelUISuperFuel;
    private TextureProgressBar fuelUISuperFuelBar;
    private Label fuelUICharge;
    private TextureProgressBar fuelUIChargeBar;

    private SpaceEnvironment spaceEnvironment; // Environment and Related Attributes
    private SpaceEnvironment.SolarState solarStatus;
    private Label envUITime;
    private Label envUIDate;
    private Label envUISolarStatus;
    private Label envUIGridRef;

    private Label flightUIFMode;
    private Label flightUIEMode;
    private Label flightUIEAMode;
    private Label flightUIVelocity;

    private Weapon weapon;
    private Label weaponUICurrent;
    private Label weaponUIClip;
    private Label weaponUIPistolAmmo;
    private Label weaponUIShotgunAmmo;

    private ProgressBar progressBar;
    private Label progressTask;
    private string taskName;
    private float progress;
    private float elapsedTime;
    private float taskDuration;

    public override void _Ready()
    {
        playerShip = GetNode<PlayerShip>("/root/Game/Space/PlayerShip");
        playerEngines = playerShip.engines;
        spaceEnvironment = GetNode<SpaceEnvironment>("/root/Game/Space/SpaceEnvironment");

        statsUIHealth = GetNode<Label>("UIBackG/HBoxC/PanelCon/GridC/HealthMC/HealthBox/GridC/SecPanel/HealthNum");
        statsUIHealthBar = GetNode<TextureProgressBar>("UIBackG/HBoxC/PanelCon/GridC/HealthMC/HealthBox/GridC/SecPanel/HealthBar");
        statsUIShield = GetNode<Label>("UIBackG/HBoxC/PanelCon/GridC/HealthMC/HealthBox/GridC2/SecPanel/ShieldNum");
        statsUIShieldBar = GetNode<TextureProgressBar>("UIBackG/HBoxC/PanelCon/GridC/HealthMC/HealthBox/GridC2/SecPanel/ShieldBar");

        fuelUIFuel = GetNode<Label>("UIBackG/HBoxC/PanelCon2/GridC/FuelMC/FuelBox/GridC/SecPanel/FuelNum");
        fuelUIFuelBar = GetNode<TextureProgressBar>("UIBackG/HBoxC/PanelCon2/GridC/FuelMC/FuelBox/GridC/SecPanel/FuelBar");
        fuelUISuperFuel = GetNode<Label>("UIBackG/HBoxC/PanelCon2/GridC/FuelMC/FuelBox/GridC2/SecPanel/SuperFuelNum");
        fuelUISuperFuelBar = GetNode<TextureProgressBar>("UIBackG/HBoxC/PanelCon2/GridC/FuelMC/FuelBox/GridC2/SecPanel/SuperFuelBar");
        fuelUICharge = GetNode<Label>("UIBackG/HBoxC/PanelCon2/GridC/FuelMC/FuelBox/GridC3/SecPanel/ChargeNum");
        fuelUIChargeBar = GetNode<TextureProgressBar>("UIBackG/HBoxC/PanelCon2/GridC/FuelMC/FuelBox/GridC3/SecPanel/ChargeBar");

        envUITime = GetNode<Label>("UIBackG/HBoxC/PanelCon3/GridC/EnvMC/EnvBox/GridC/SecPanel/TimeNum");
        envUIDate = GetNode<Label>("UIBackG/HBoxC/PanelCon3/GridC/EnvMC/EnvBox/GridC/SecPanel/DateNum");
        envUISolarStatus = GetNode<Label>("UIBackG/HBoxC/PanelCon3/GridC/EnvMC/EnvBox/GridC2/SecPanel/SolarStatus");
        envUIGridRef = GetNode<Label>("UIBackG/HBoxC/PanelCon3/GridC/EnvMC/EnvBox/GridC3/SecPanel/GridRef");

        flightUIFMode = GetNode<Label>("UIBackG/HBoxC/PanelCon4/GridC/FlightMC/FlightBox/GridC/SecPanel/FlightMode");
        flightUIEMode = GetNode<Label>("UIBackG/HBoxC/PanelCon4/GridC/FlightMC/FlightBox/GridC2/SecPanel/EngineMode");
        flightUIEAMode = GetNode<Label>("UIBackG/HBoxC/PanelCon4/GridC/FlightMC/FlightBox/GridC2/SecPanel/EngineAfterBurner");
        flightUIVelocity = GetNode<Label>("UIBackG/HBoxC/PanelCon4/GridC/FlightMC/FlightBox/GridC3/SecPanel/VelocityNum");

        weaponUICurrent = GetNode<Label>("UIBackG/HBoxC/PanelCon5/GridC/WeaponMC/WeaponBox/GridC/SecPanel/CurrentWeapon");
        weaponUIClip = GetNode<Label>("UIBackG/HBoxC/PanelCon5/GridC/WeaponMC/WeaponBox/GridC2/SecPanel/CurrentClip");

        playerShip.StatsMaxUpdate += (MaxIntegrity, MaxShield, MaxFuel, MaxSuperFuel, MaxElectricCharge) => UpdateMaxStatsUI(MaxIntegrity, MaxShield, MaxFuel, MaxSuperFuel, MaxElectricCharge);
        playerShip.StatsUpdate += (Integrity, Shield, Fuel, SuperFuel, ElectricCharge, Velocity) => UpdateStatsUI(Integrity, Shield, Fuel, SuperFuel, ElectricCharge, Velocity);

        spaceEnvironment.TimeUpdate += (Minute, Hour, Day, Year) => UpdateTimeUI(Minute, Hour, Day, Year);
        spaceEnvironment.SolarUpdate += (SolarStatus, NextSolarStatus, transition) => UpdateSolarUI(SolarStatus, NextSolarStatus, transition); ;

        playerShip.FlightModeUpdate += (FlightMode) => flightUIFMode.Text = FlightMode.ToString().ToUpper();
        playerEngines.EngineFixedState += (FixedState) => UpdateEngineModeUI(FixedState);

        playerShip.GridRefUpdate += (GridRef) => envUIGridRef.Text = $"X:{GridRef.X} Y:{GridRef.Y}";

        playerShip.WeaponUpdate += (WeaponType) =>
        {
            UpdateWeaponUI(WeaponType);
            weapon = playerShip.Weapon;
            weapon.ClipUpdate += (int currentClip, int ammoCapacity) =>
            {
                UpdateAmmoUI(currentClip, ammoCapacity);
            };
        };

        playerShip.ShipTimedAction += (taskName, taskDuration) => StartTimedAction(taskName, taskDuration);
        progressBar = GetNode<ProgressBar>("ProgressBar");
        progressTask = GetNode<Label>("ProgressTask");
    }

    public override void _Process(double delta)
    {
    }

    private void UpdateMaxStatsUI(float MaxIntegrity, float MaxShield, float MaxFuel, float MaxSuperFuel, float MaxElectricCharge)
    {
        statsUIHealthBar.MaxValue = MaxIntegrity;
        statsUIShieldBar.MaxValue = MaxShield;
        fuelUIFuelBar.MaxValue = MaxFuel;
        fuelUISuperFuelBar.MaxValue = MaxSuperFuel;
        fuelUIChargeBar.MaxValue = MaxElectricCharge;
    }

    private void UpdateStatsUI(float Integrity, float Shield, float Fuel, float SuperFuel, float ElectricCharge, float Velocity)
    {
        statsUIHealth.Text = $"{Integrity:F2}";
        statsUIHealthBar.Value = Integrity;
        statsUIShield.Text = $"{Shield:F2}";
        statsUIShieldBar.Value = Shield;
        fuelUIFuel.Text = $"{Fuel:F2}";
        fuelUIFuelBar.Value = Fuel;
        fuelUISuperFuel.Text = $"{SuperFuel:F2}";
        fuelUISuperFuelBar.Value = SuperFuel;
        fuelUICharge.Text = $"{ElectricCharge:F2}";
        fuelUIChargeBar.Value = ElectricCharge;
        flightUIVelocity.Text = $"{Velocity:F2}/ms";
    }

    private void UpdateTimeUI(int Minute, int Hour, int Day, int Year)
    {
        envUITime.Text = $"{Hour:D2}:{Minute:D2}";
        envUIDate.Text = $"{Day:D2}/30{Year:D2}";
    }

    private void UpdateSolarUI(SpaceEnvironment.SolarState solarStatus, SpaceEnvironment.SolarState NextSolarStatus, bool transition)
    {
        if (transition)
        {
            envUISolarStatus.Text = $"-> " + NextSolarStatus.ToString().ToUpper();
        }
        else
        {
            envUISolarStatus.Text = solarStatus.ToString().ToUpper();
        }
    }

    private void UpdateEngineModeUI(PlayerEngines.FixedState fixedState)
    {
        switch (fixedState)
        {
            case PlayerEngines.FixedState.Normal:
                flightUIEAMode.Visible = false;
                flightUIEMode.Visible = true;
                flightUIEMode.Text = "NORMAL";
                break;
            case PlayerEngines.FixedState.Landing:
                flightUIEAMode.Visible = false;
                flightUIEMode.Visible = true;
                flightUIEMode.Text = "LANDING";
                break;
            case PlayerEngines.FixedState.Afterburner:
                flightUIEMode.Visible = false;
                flightUIEAMode.Visible = true;
                flightUIEAMode.Text = "AFTERBURNER";
                break;
        }
    }

    private void UpdateWeaponUI(int weaponType)
    {
        string weaponTypeName = ((PlayerWeaponFactory.Type)weaponType).ToString();
        weaponUICurrent.Text = weaponTypeName.ToUpper();
    }

    private void UpdateAmmoUI(int currentClip, int ammoCapacity)
    {
        weaponUIClip.Text = $"{currentClip} / {ammoCapacity}";
    }

    private void StartTimedAction(string taskName, float taskDuration)
    {
        progressTask.Text = taskName;
        elapsedTime = 0f;
        progressBar.MaxValue = taskDuration;
        SetProcess(true);
    }

    private void StopTimedAction()
    {
        progressTask.Text = "";
        SetProcess(false);
    }
}