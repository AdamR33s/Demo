using System;
using System.Collections.Generic;
using Godot;


public partial class PlayerShip : CharacterBody2D
{
	class Hull
	{
		public CharacterBody2D instance;
		public AnimationPlayer animPlayer;
		public Sprite2D sprite;
	}

	class Engines
	{
		public CharacterBody2D instance;
		public AnimationPlayer animPlayer;
		public Sprite2D sprite;
	}

	class LandingGear
	{
		public CharacterBody2D instance;
		public AnimationPlayer animPlayer;
		public Sprite2D sprite;
	}

	//Martian Signals
	[Signal] public delegate void StatsUpdateEventHandler(float health, float fuel); // Signal for refreshing stats after change / degrade
	[Signal] public delegate void WeaponUpdateEventHandler(int WeaponType);
	[Signal] public delegate void ShipTimedActionEventHandler(string taskName, float taskDuration); // Timed Action Signal

	private Vector2 mousePostion = new();
	private Vector2 direction = new();
	private Vector2 strafeDirection = new();
	private Hull hull = new();
	private Engines engines = new();
	private LandingGear landingGear = new();
	public State state;
	public Node2D crosshair;
	private float crosshairDistance = 200.0f;

	public enum State
	{
		idle,
		moving,
		attacking,
		retreating,
		landing,

	}

	public enum AnimPlayers
	{
		Hull,
		Engine,
		Landing
	}

	public enum ShipStats // Setup Stats Type and Variables for Each Martian
	{
		integrity,
		fuel,
		maxspeed,
		acceleration,
		landingAcceleration,
		friction,
		agility,
		landingAgility,
		targetingspeed
	}

	private enum ShipConfig
	{
		FlightMode,
		Crosshair,
	}

	private enum FlightMode
	{
		Utility,
		Combat,
		Landing,

	}

	[Export] public float integrity { get; private set; } = 100.00f;
	[Export] public float maxspeed { get; private set; } = 500.00f;
	[Export] public float fuel { get; private set; } = 100.00f;
	[Export] public float acceleration { get; private set; } = 500.00f;
	[Export] public float landingAcceleration { get; private set; } = 200.00f;
	[Export] public float friction { get; private set; } = 0.20f;
	[Export] public float agility { get; private set; } = 0.5f;
	[Export] public float landingAgility { get; private set; } = 0.3f;
	[Export] public float targetingSpeed { get; private set; } = 1.0f;


	[Export] private FlightMode flightmode;
	public Weapon weapon; // Current Weapon
	private Node2D weaponSlot; // Current Weapon Slot

	public override void _Ready() // Generate Stats & Skills on Instantiation, 
	{
		hull.instance = GetNode<CharacterBody2D>("Hull");
		hull.animPlayer = GetNode<AnimationPlayer>("Hull/AnimPlayer");
		hull.sprite = GetNode<Sprite2D>("Hull/HullSprite");
		engines.instance = GetNode<CharacterBody2D>("Engines");
		engines.animPlayer = GetNode<AnimationPlayer>("Engines/AnimPlayer");
		engines.sprite = GetNode<Sprite2D>("Engines/EnginesSprite");
		landingGear.instance = GetNode<CharacterBody2D>("LandingGear");
		landingGear.animPlayer = GetNode<AnimationPlayer>("LandingGear/AnimPlayer");
		landingGear.sprite = GetNode<Sprite2D>("LandingGear/LandingGearSprite");

		flightmode = FlightMode.Combat; // TODO - REMOVE AFTER TESTING

		EmitSignal(SignalName.StatsUpdate, integrity, fuel); // Stats Update Signal
		EquipWeapon(WeaponFactory.Type.Pistol);
		updateShipAnims();
	}

	public override void _PhysicsProcess(double delta)
	{
		mousePostion = GetGlobalMousePosition();
		checkInput();
		updateShipAnims();
		updateFlight(mousePostion, delta);
		updateCrosshair(mousePostion, delta);
	}

	public void checkInput()
	{
		if (Input.IsActionJustPressed("ui_shoot"))
		{
			weapon.Shoot(Velocity);
			GD.Print("Fired One Shot Call");
		}
		if (Input.IsActionJustPressed("ui_flightmode"))
		{
			ChangeFlightMode();
		}
		if (Input.IsActionJustPressed("ui_landing"))
		{
			flightmode = FlightMode.Landing;
			crosshair.Visible = false;
			landingGear.sprite.Visible = true;
			landingGear.animPlayer.Play("deploy");
		}
	}

	public void ChangeFlightMode()
	{
		switch (flightmode)
		{
			case FlightMode.Utility:
				flightmode = FlightMode.Combat;
				crosshair.Visible = true;
				break;
			case FlightMode.Combat:
				flightmode = FlightMode.Utility;
				crosshair.Visible = false;
				break;
			case FlightMode.Landing:
				flightmode = FlightMode.Utility;
				break;
		};
	}

	public void updateCrosshair(Vector2 mousePostion, double delta)
	{
		var angleDifference = GetAngleTo(mousePostion);
		var clampedAngle = Rotation + Mathf.Clamp(angleDifference, -Mathf.DegToRad(15), +Mathf.DegToRad(15));
		// Convert the angle to a unit vector
		var direction = new Vector2(Mathf.Cos(clampedAngle), Mathf.Sin(clampedAngle));
		// Move the crosshair towards the direction
		crosshair.Position = Position + direction * crosshairDistance;
	}

	public void updateFlight(Vector2 mousePostion, double delta)
	{
		switch (flightmode)
		{
			case FlightMode.Utility:
				shipHeadingUtility(delta);
				break;
			case FlightMode.Combat:
				shipHeadingCombat(delta);
				break;
			case FlightMode.Landing:
				shipHeadingLanding(delta);
				break;
		}
	}

	public void shipHeadingCombat(double delta)
	{
		var headingDifference = GetAngleTo(mousePostion);
		if (Mathf.Abs(headingDifference) > (float)0.01)
		{
			Rotate(headingDifference * (float)delta * agility);
		}
		shipMovementCombat(delta);
	}

	public void shipMovementCombat(double delta)
	{
		direction = (mousePostion - GlobalPosition).Normalized();
		if (!Input.IsActionPressed("ui_up"))
		{
			// If "ui_up" is not pressed, apply friction to slow down the ship
			if (Velocity.Length() > (friction * delta))
			{
				Velocity *= (float)Mathf.Pow(1.0 - friction, delta);
			}
			else
			{
				Velocity = Vector2.Zero;
			}
		}
		else
		{
			// If "ui_up" is pressed, accelerate the ship in the given direction
			Velocity += direction * (float)(acceleration * delta);
			fuel -= 0.01f * 60.0f * (float)delta;
		}

		// Limit the velocity to the maximum speed
		Velocity = Velocity.LimitLength(maxspeed);

		// Move the ship
		MoveAndSlide();
		EmitSignal(SignalName.StatsUpdate, integrity, fuel);
	}

	public void shipHeadingUtility(double delta)
	{
		if (Input.IsActionPressed("ui_left"))
		{
			Rotate(-agility * (float)delta);
		}
		if (Input.IsActionPressed("ui_right"))
		{
			Rotate(agility * (float)delta);
		}
		shipMovementUtility(delta);
	}

	public void shipMovementUtility(double delta) // KEYBOARD MOVEMENT
	{
		direction = new Vector2(1, 0).Rotated(Rotation).Normalized();
		if (Input.IsActionPressed("ui_up"))
		{
			// If "ui_up" is pressed, accelerate the ship in the given direction
			Velocity += direction * (float)(acceleration * delta);
			fuel -= 0.01f * 60.0f * (float)delta;
		}
		else
		{
			// If "ui_up" is not pressed, apply friction to slow down the ship
			if (Velocity.Length() > (friction * delta))
			{
				Velocity *= (float)Mathf.Pow(1.0 - friction, delta);
			}
			else
			{
				Velocity = Vector2.Zero;
			}
		}

		// Limit the velocity to the maximum speed
		Velocity = Velocity.LimitLength(maxspeed);
		// Move the ship
		MoveAndSlide();
		EmitSignal(SignalName.StatsUpdate, integrity, fuel);
	}

	private void shipHeadingLanding(double delta)
	{
		if (Input.IsActionPressed("ui_thrustleft"))
		{
			Rotate(-landingAgility * (float)delta);
		}
		if (Input.IsActionPressed("ui_thrustright"))
		{
			Rotate(landingAgility * (float)delta);
		}
		shipMovementLanding(delta);
	}

	private void shipMovementLanding(double delta)
	{
		// Move the ship towards the landing pad
		direction = new Vector2(1, 0).Rotated(Rotation).Normalized();
		strafeDirection = new Vector2(0, -1).Rotated(Rotation).Normalized();
		if (Input.IsActionPressed("ui_up"))
		{
			// If "ui_up" is pressed, accelerate the ship in the given direction
			Velocity += direction * (float)(landingAcceleration * delta);
			fuel -= 0.01f * 60.0f * (float)delta;
		}
		else if (Input.IsActionPressed("ui_down"))
		{
			Velocity -= direction * (float)(landingAcceleration * delta);
			fuel -= 0.01f * 60.0f * (float)delta;
		}
		else if (Input.IsActionPressed("ui_left") && !Input.IsKeyLabelPressed(Key.Shift))
		{
			Velocity += strafeDirection * (float)(landingAcceleration * delta);
			fuel -= 0.01f * 60.0f * (float)delta;
		}
		else if (Input.IsActionPressed("ui_right") && !Input.IsKeyLabelPressed(Key.Shift))
		{
			Velocity -= strafeDirection * (float)(landingAcceleration * delta);
			fuel -= 0.01f * 60.0f * (float)delta;
		}
		else
		{
			// Apply friction to slow down the ship
			if (Velocity.Length() > (friction * delta))
			{
				Velocity *= (float)Mathf.Pow(1.0 - friction, delta);
			}
			else
			{
				Velocity = Vector2.Zero;
			}
		}
		// Limit the velocity to the maximum speed
		Velocity = Velocity.LimitLength(maxspeed);
		// Move the ship
		MoveAndSlide();
		EmitSignal(SignalName.StatsUpdate, integrity, fuel);
	}

	private void updateShipAnims()
	{
		updateHullAnim();
		updateEngineAnim();
	}

	private void updateHullAnim()
	{
	}

	private void updateEngineAnim()
	{
		if (Input.IsActionPressed("ui_up"))
		{
			engines.animPlayer.Play("moving");
		}
		else
		{
			engines.animPlayer.Play("idle");
		}
	}

	public void ImproveStats(ShipStats statType, float amount)
	{
		switch (statType)
		{
			case ShipStats.integrity:
				integrity += amount;
				break;
			case ShipStats.fuel:
				fuel += amount;
				break;
		}
		EmitSignal(SignalName.StatsUpdate, integrity, fuel);
	}

	public void ErodeStats(ShipStats statType, float amount)
	{
		switch (statType)
		{
			case ShipStats.integrity:
				integrity -= amount;
				break;
			case ShipStats.fuel:
				fuel -= amount;
				break;
		}
		EmitSignal(SignalName.StatsUpdate, integrity, fuel);
	}

	public void EquipWeapon(WeaponFactory.Type weaponType)
	{
		if (weapon != null)
		{
			weapon.QueueFree();
		}
		weapon = WeaponFactory.LoadWeapon(weaponType);
		weaponSlot = GetNode<Node2D>("WeaponSlot");
		weaponSlot.AddChild(weapon);
		EmitSignal(SignalName.WeaponUpdate, (int)weaponType);
		weapon.OnEquip();
	}
}
