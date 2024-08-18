using Godot;

public partial class PlayerShip : CharacterBody2D
{
	// PlayerShip Signals
	[Signal] public delegate void StatsUpdateEventHandler(float Integrity, float Shield, float Fuel, float SuperFuel, float ElectricCharge, float Velocity); // Signal for refreshing stats after change / degrade
	[Signal] public delegate void StatsMaxUpdateEventHandler(float MaxIntegrity, float MaxShield, float MaxFuel, float MaxSuperFuel, float MaxElectricCharge); // Signal for refreshing stats after change / degrade
	[Signal] public delegate void FlightModeUpdateEventHandler(PlayerShipFlightMode flightMode); // Signal for changing weapon
	[Signal] public delegate void WeaponUpdateEventHandler(int WeaponType);
	[Signal] public delegate void GridRefUpdateEventHandler(Vector2 position);
	[Signal] public delegate void ShipTimedActionEventHandler(string taskName, float taskDuration); // Timed Action Signal

	public class PlayerShipConfig
	{
		public float CrosshairDistance { get; private set; } = 200.0f;
	}

	public class PlayerShipAttr
	{
		public float Acceleration { get; private set; } = 500.00f;
		public float LandingAcceleration { get; private set; } = 200.00f;
		public float Agility { get; private set; } = 0.5f;
		public float LandingAgility { get; private set; } = 0.3f;
		public float TargetingSpeed { get; private set; } = 1.0f;
		public float Friction { get; private set; } = 0.10f;
	}

	public enum PlayerShipFlightMode
	{
		Utility,
		Combat,
		Landing,
	}

	private Vector2 mousePosition = new();
	private Vector2 direction = new();
	private Node2D weaponSlot; // Current Weapon Slot
	private PlayerShipFlightMode flightMode;
	private KinematicCollision2D playerShipCollision;
	private Hull hull;
	private PlayerEngines engines;
	private PlauyerLandingGear landingGear;
	private AnimationPlayer shipAnimPlayer;

	public Weapon Weapon;
	public Node2D Crosshair;
	public Area2D Scanner;
	public CollisionShape2D ScannerArea;

	private readonly ShipStats ShipStats = new();
	public readonly PlayerShipAttr ShipAttr = new();
	public readonly PlayerShipConfig ShipConfig = new();

	public override void _Ready() // Generate Stats & Skills on Instantiation, 
	{
		// Setup Ship Components
		hull = GetNode<Hull>("Hull");
		engines = GetNode<PlayerEngines>("PlayerEngines");
		landingGear = new PlauyerLandingGear();
		landingGear.AnimPlayer = GetNode<AnimationPlayer>("LGAnimPlayer");
		shipAnimPlayer = GetNode<AnimationPlayer>("ShipAnimPlayer");

		// Collision Setup
		hull.cB = GetNode<CollisionPolygon2D>("HullCB");
		engines.e1cB = GetNode<CollisionPolygon2D>("Engine1CB");
		engines.e2cB = GetNode<CollisionPolygon2D>("Engine2CB");
		landingGear.cB1 = GetNode<CollisionPolygon2D>("LGCB1");
		landingGear.cB2 = GetNode<CollisionPolygon2D>("LGCB2");

		// Setup Ship Components
		Scanner = GetNode<Area2D>("Scanner");
		ScannerArea = GetNode<CollisionShape2D>("Scanner/ScannerArea");

		// Setup Ship Config
		ShipStats.CurrentFuel.Change(Fuels.Type.Hydrazine);
		ShipStats.CurrentFuel.Add(100.0f, ShipStats.MaxFuel);
		ShipStats.CurrentSuperFuel.Change(SuperFuels.Type.LH2LOX);
		ShipStats.CurrentSuperFuel.Add(100.0f, ShipStats.MaxSuperFuel);
		flightMode = PlayerShipFlightMode.Combat; // TODO - REMOVE AFTER TESTING

		// Setup Ship Stats and Start Anims
		EmitSignal(SignalName.StatsMaxUpdate, ShipStats.Integrity, ShipStats.Shield, ShipStats.CurrentFuel.Amount, ShipStats.CurrentSuperFuel.Amount, ShipStats.ElectricCharge, Velocity.Length()); // Stats Max Update Signal
		EmitSignal(SignalName.StatsUpdate, ShipStats.Integrity); // Stats Update Signal
		EmitSignal(SignalName.FlightModeUpdate, (int)flightMode); // Flight Mode Update Signal
		EquipWeapon(PlayerWeaponFactory.Type.Blaster);
	}

	public override void _PhysicsProcess(double delta)
	{
		mousePosition = GetGlobalMousePosition();
		checkInput();
		updateFlight(delta);
	}

	public override void _Process(double delta)
	{
		updateCrosshair(mousePosition);
		EmitSignal(SignalName.GridRefUpdate, GlobalPosition);
	}

	public void checkInput()
	{
		if (Input.IsActionJustPressed("ui_flightmode") || Input.IsActionJustPressed("ui_landing"))
		{
			ChangeFlightMode(Input.IsActionJustPressed("ui_landing"));
		}
		if ((flightMode == PlayerShipFlightMode.Utility || flightMode == PlayerShipFlightMode.Combat) && Input.IsActionJustPressed("ui_afterburner"))
		{
			if (engines.fixedState == PlayerEngines.FixedStates.Afterburner)
			{
				engines.ChangeFixedState(PlayerEngines.FixedStates.Normal);
			}
			else
			{
				engines.ChangeFixedState(PlayerEngines.FixedStates.Afterburner);
			}
		}
		if (Input.IsActionJustPressed("ui_shoot"))
		{
			Weapon.Shoot(Velocity);
			GD.Print("Fired One Shot Call");
		}
	}

	public void ChangeFlightMode(bool isLanding = false)
	{
		if (isLanding)
		{
			flightMode = PlayerShipFlightMode.Landing;
			hull.SetLandingMode();
			engines.ChangeFixedState(PlayerEngines.FixedStates.Landing);
			landingGear.SetLandingMode();
			Crosshair.Visible = false;
		}
		else
			switch (flightMode)
			{
				case PlayerShipFlightMode.Utility:
					flightMode = PlayerShipFlightMode.Combat;
					hull.SetCombatMode();
					engines.ChangeFixedState(PlayerEngines.FixedStates.Normal);
					landingGear.SetCombatMode();
					Crosshair.Visible = true;
					break;
				case PlayerShipFlightMode.Combat:
					flightMode = PlayerShipFlightMode.Utility;
					hull.SetUtilityMode();
					engines.ChangeFixedState(PlayerEngines.FixedStates.Normal);
					landingGear.SetUtilityMode();
					Crosshair.Visible = false;
					break;
				case PlayerShipFlightMode.Landing:
					flightMode = PlayerShipFlightMode.Utility;
					hull.SetUtilityMode();
					engines.ChangeFixedState(PlayerEngines.FixedStates.Normal);
					landingGear.SetUtilityMode();
					Crosshair.Visible = false;
					break;
			};
		EmitSignal(SignalName.FlightModeUpdate, (int)flightMode);
	}

	public void updateCrosshair(Vector2 mousePostion)
	{
		var angleDifference = GetAngleTo(mousePostion);
		var clampedAngle = Rotation + Mathf.Clamp(angleDifference, -Mathf.DegToRad(15), +Mathf.DegToRad(15));
		// Convert the angle to a unit vector
		direction = Vector2.FromAngle(clampedAngle);
		// Move the crosshair towards the direction
		Crosshair.Position = Position + direction * ShipConfig.CrosshairDistance;
	}

	public void updateFlight(double delta)
	{
		switch (flightMode)
		{
			case PlayerShipFlightMode.Utility:
				shipHeadingUtility(delta);
				shipMovementUtility(delta);
				break;
			case PlayerShipFlightMode.Combat:
				shipHeadingCombat(delta);
				shipMovementCombat(delta);
				break;
			case PlayerShipFlightMode.Landing:
				shipHeadingLanding(delta);
				shipMovementLanding(delta);
				break;
		}
	}

	public void shipHeadingCombat(double delta)
	{
		var headingDifference = GetAngleTo(mousePosition);
		if (Mathf.Abs(headingDifference) > (float)0.01)
		{
			Rotate(headingDifference * (float)delta * ShipAttr.Agility);
		}
	}

	public void shipMovementCombat(double delta)
	{
		direction = Vector2.FromAngle(Rotation);
		if (Input.IsActionPressed("ui_up") && engines.fixedState == PlayerEngines.FixedStates.Afterburner)
		{
			if (engines.liveState == PlayerEngines.LiveStates.Idle)
			{
				engines.ChangeLiveState(PlayerEngines.LiveStates.Accelerating);
			}
			Velocity += direction * (float)((ShipStats.CurrentFuel.Acceleration + ShipStats.CurrentSuperFuel.Acceleration) * delta);
			ShipStats.CurrentFuel.Burn((float)delta);
			ShipStats.CurrentSuperFuel.Burn((float)delta);
			Velocity = Velocity.LimitLength(ShipStats.CurrentFuel.MaxSpeed + ShipStats.CurrentSuperFuel.MaxSpeed);

		}
		else
		if (Input.IsActionPressed("ui_up"))
		{
			if (engines.liveState == PlayerEngines.LiveStates.Idle)
			{
				engines.ChangeLiveState(PlayerEngines.LiveStates.Accelerating);
			}
			// If "ui_up" is pressed, accelerate the ship in the given direction
			Velocity += direction * (float)(ShipStats.CurrentFuel.Acceleration * delta);
			ShipStats.CurrentFuel.Burn((float)delta);
			Velocity = Velocity.LimitLength(ShipStats.CurrentFuel.MaxSpeed);
		}
		else
		{
			if (engines.liveState == PlayerEngines.LiveStates.Accelerating)
			{
				engines.ChangeLiveState(PlayerEngines.LiveStates.Idle);
			}
			// If "ui_up" is not pressed, apply friction to slow down the ship
			if (Velocity.Length() > (ShipAttr.Friction * delta))
			{
				Velocity *= (float)Mathf.Pow(1.0 - ShipAttr.Friction, delta);
			}
			else
			{
				Velocity = Vector2.Zero;
			}
		}
		playerShipCollision = MoveAndCollide(Velocity * (float)delta);
		if (playerShipCollision != null)
		{
			var hitinfo = playerShipCollision.GetCollider();
			var localShape = playerShipCollision.GetLocalShape();
			GD.Print(" Local Shape: ", localShape);
			if (hitinfo is StaticBody2D)
			{
				Velocity = Velocity.Bounce(playerShipCollision.GetNormal());
			}
		}
		EmitSignal(SignalName.StatsUpdate, ShipStats.Integrity, ShipStats.Shield, ShipStats.CurrentFuel.Amount, ShipStats.CurrentSuperFuel.Amount, ShipStats.ElectricCharge, Velocity.Length());
	}

	public void shipHeadingUtility(double delta)
	{
		if (Input.IsActionPressed("ui_left"))
		{
			Rotate(-ShipAttr.Agility * (float)delta);
		}
		if (Input.IsActionPressed("ui_right"))
		{
			Rotate(ShipAttr.Agility * (float)delta);
		}
	}

	public void shipMovementUtility(double delta) // KEYBOARD MOVEMENT
	{
		direction = new Vector2(1, 0).Rotated(Rotation).Normalized();

		if (Input.IsActionPressed("ui_up") && engines.fixedState == PlayerEngines.FixedStates.Afterburner)
		{
			if (engines.liveState == PlayerEngines.LiveStates.Idle)
			{
				engines.ChangeLiveState(PlayerEngines.LiveStates.Accelerating);
			}
			Velocity += direction * (float)((ShipStats.CurrentFuel.Acceleration + ShipStats.CurrentSuperFuel.Acceleration) * delta);
			ShipStats.CurrentFuel.Burn((float)delta);
			ShipStats.CurrentSuperFuel.Burn((float)delta);
			Velocity = Velocity.LimitLength(ShipStats.CurrentFuel.MaxSpeed + ShipStats.CurrentSuperFuel.MaxSpeed);
		}
		else
		if (Input.IsActionPressed("ui_up"))
		{
			if (engines.liveState == PlayerEngines.LiveStates.Idle)
			{
				engines.ChangeLiveState(PlayerEngines.LiveStates.Accelerating);
			}
			// If "ui_up" is pressed, accelerate the ship in the given direction
			Velocity += direction * (float)(ShipStats.CurrentFuel.Acceleration * delta);
			ShipStats.CurrentFuel.Burn((float)delta);
			Velocity = Velocity.LimitLength(ShipStats.CurrentFuel.MaxSpeed);
		}
		else
		{
			if (engines.liveState == PlayerEngines.LiveStates.Accelerating)
			{
				engines.ChangeLiveState(PlayerEngines.LiveStates.Idle);
			}
			// If "ui_up" is not pressed, apply friction to slow down the ship
			if (Velocity.Length() > (ShipAttr.Friction * delta))
			{
				Velocity *= (float)Mathf.Pow(1.0 - ShipAttr.Friction, delta);
			}
			else
			{
				Velocity = Vector2.Zero;
			}
		}
		MoveAndCollide(Velocity * (float)delta);
		EmitSignal(SignalName.StatsUpdate, ShipStats.Integrity, ShipStats.Shield, ShipStats.CurrentFuel.Amount, ShipStats.CurrentSuperFuel.Amount, ShipStats.ElectricCharge, Velocity.Length());
	}

	private void shipHeadingLanding(double delta)
	{
		if (Input.IsActionPressed("ui_thrustleft"))
		{
			Rotate(-ShipAttr.LandingAgility * (float)delta);
		}
		if (Input.IsActionPressed("ui_thrustright"))
		{
			Rotate(ShipAttr.LandingAgility * (float)delta);
		}
	}

	private void shipMovementLanding(double delta)
	{
		// Move the ship towards the landing pad
		direction = new Vector2(1, 0).Rotated(Rotation).Normalized();
		var strafeDirection = new Vector2(0, -1).Rotated(Rotation).Normalized();
		if (Input.IsActionPressed("ui_up"))
		{
			// If "ui_up" is pressed, accelerate the ship in the given direction
			Velocity += direction * (float)(ShipStats.CurrentFuel.Acceleration * delta);
			ShipStats.CurrentFuel.Burn((float)delta);
		}
		else if (Input.IsActionPressed("ui_down"))
		{
			Velocity -= direction * (float)(ShipStats.CurrentFuel.Acceleration * delta);
			ShipStats.CurrentFuel.Burn((float)delta);
		}
		else if (Input.IsActionPressed("ui_left") && !Input.IsKeyLabelPressed(Key.Shift))
		{
			Velocity += strafeDirection * (float)(ShipStats.CurrentFuel.Acceleration * delta);
			ShipStats.CurrentFuel.Burn((float)delta);
		}
		else if (Input.IsActionPressed("ui_right") && !Input.IsKeyLabelPressed(Key.Shift))
		{
			Velocity -= strafeDirection * (float)(ShipStats.CurrentFuel.Acceleration * delta);
			ShipStats.CurrentFuel.Burn((float)delta);
		}
		else
		{
			// Apply friction to slow down the ship
			if (Velocity.Length() > (ShipAttr.Friction * delta))
			{
				Velocity *= (float)Mathf.Pow(1.0 - ShipAttr.Friction, delta);
			}
			else
			{
				Velocity = Vector2.Zero;
			}
		}
		// Limit the velocity to the maximum speed
		Velocity = Velocity.LimitLength(ShipStats.CurrentFuel.MaxSpeed);
		// Move the ship
		playerShipCollision = MoveAndCollide(Velocity * (float)delta);
		if (playerShipCollision != null)
		{
			var hitinfo = playerShipCollision.GetCollider();
			var localShape = playerShipCollision.GetLocalShape();
			GD.Print(" Local Shape: ", localShape.ToString());
		}
		EmitSignal(SignalName.StatsUpdate, ShipStats.Integrity, ShipStats.Shield, ShipStats.CurrentFuel.Amount, ShipStats.CurrentSuperFuel.Amount, ShipStats.ElectricCharge, Velocity.Length());
	}

	public void EquipWeapon(PlayerWeaponFactory.Type weaponType)
	{
		Weapon?.QueueFree();
		Weapon = PlayerWeaponFactory.LoadWeapon(weaponType);
		weaponSlot = GetNode<Node2D>("WeaponSlot");
		weaponSlot.AddChild(Weapon);
		EmitSignal(SignalName.WeaponUpdate, (int)weaponType);
		Weapon.OnEquip();
	}
}