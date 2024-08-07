using System;
using Godot;

public partial class SpaceUI : CanvasLayer
{
    private PlayerShip playerShip; // Martian and Related Attributes
    private Timer updateUITimer;
    private Label statsUIHealth;
    private TextureProgressBar statsUIHealthBar;
    private TextureProgressBar statsUIFuelBar;

    private Label statsUIFuel;

    private Label skillsUIAiming;
    private Label skillsUIScavenging;
    private Label skillsUIRepairs;

    private Weapon weapon;
    private Label weaponUICurrent;
    private Label weaponUIClip;
    private Label weaponUIPistolAmmo;
    private Label weaponUIShotgunAmmo;

    private Environment spaceEnvironment; // Environment and Related Attributes
    public int day;
    private Environment.SolarType solarStatus;
    private Label envUIDay;
    private Label envUISolarStatus;

    private ProgressBar progressBar;
    private Label progressTask;
    private string taskName;
    private float progress;
    private float elapsedTime;
    private float taskDuration;

    public override void _Ready()
    {
        playerShip = GetNode<PlayerShip>("/root/Game/Space/PlayerShip");
        spaceEnvironment = GetNode<Environment>("/root/Game/Environment");

        statsUIHealth = GetNode<Label>("UIBackG/HBoxC/PanelCon/GridC/HealthMC/HealthBox/HealthNum");
        statsUIHealthBar = GetNode<TextureProgressBar>("UIBackG/HBoxC/PanelCon/GridC/HealthMC/HealthBox/HealthBar");
        statsUIFuel = GetNode<Label>("UIBackG/HBoxC/PanelCon/GridC/FuelMC/FuelBox/FuelNum");
        statsUIFuelBar = GetNode<TextureProgressBar>("UIBackG/HBoxC/PanelCon/GridC/FuelMC/FuelBox/FuelBar");

        envUIDay = GetNode<Label>("UIBackG/HBoxC/PanelCon2/GridC/EnvMC/EnvBox/DayNum");
        envUISolarStatus = GetNode<Label>("UIBackG/HBoxC/PanelCon2/GridC/EnvMC/EnvBox/SolarStatus");

        weaponUICurrent = GetNode<Label>("UIBackG/HBoxC/PanelCon3/GridC/WeaponMC/WeaponBox/CurrentWeapon");
        weaponUIClip = GetNode<Label>("UIBackG/HBoxC/PanelCon3/GridC/WeaponMC/WeaponBox/CurrentClip");

        playerShip.StatsUpdate += (integrity, fuel) => UpdateStatsUI(integrity, fuel);
        playerShip.WeaponUpdate += (weaponType) =>
        {
            UpdateWeaponUI(weaponType);
            weapon = playerShip.weapon;
            weapon.ClipUpdate += (int currentClip, int ammoCapacity) =>
            {
                UpdateAmmoUI(currentClip, ammoCapacity);
            };
        };

        spaceEnvironment.EnvironmentUpdate += (day, solarStatus) => UpdateEnvironmentUI(day, solarStatus);

        playerShip.ShipTimedAction += (taskName, taskDuration) => StartTimedAction(taskName, taskDuration);
        progressBar = GetNode<ProgressBar>("ProgressBar");
        progressTask = GetNode<Label>("ProgressTask");
    }

    public override void _Process(double delta)
    {
        elapsedTime += (float)delta;
        progress = elapsedTime / taskDuration;
        progressBar.Value = progress;
        if (elapsedTime >= taskDuration)
        {
            StopTimedAction();
        }
    }

    private void UpdateStatsUI(float integrity, float fuel)
    {
        statsUIHealth.Text = integrity.ToString("F2");
        statsUIHealthBar.Value = integrity;
        statsUIFuel.Text = fuel.ToString("F2");
        statsUIFuelBar.Value = fuel;
    }

    private void UpdateEnvironmentUI(int day, Environment.SolarType solarStatus)
    {
        envUIDay.Text = "Day: " + day.ToString();
        envUISolarStatus.Text = "Solar: " + solarStatus.ToString();
    }

    private void UpdateWeaponUI(int weaponType)
    {
        string weaponTypeName = ((WeaponFactory.Type)weaponType).ToString();
        weaponUICurrent.Text = "Weapon: " + weaponTypeName;
    }

    private void UpdateAmmoUI(int currentClip, int ammoCapacity)
    {
        Console.WriteLine("UI Update Function Called");
        weaponUIClip.Text = $"Clip: {currentClip} / {ammoCapacity}";
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