using Godot;
using System.Collections.Generic;

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
		public float Friction { get; private set; } = 0.1f;
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
	[Export] private Inventory inventory = new();
	private PlayerShipFlightMode flightMode;


	public PlayerHull hull { get; private set; } = new();
	public PlayerEngines engines { get; private set; } = new();
	public PlayerLG landingGear { get; private set; } = new();
	public PlayerUtilArm utilArm { get; private set; }
	public Vector2I GridCoords { get; set; }
	public Weapon Weapon;
	public Node2D Crosshair;
	public Area2D Scanner;
	public CollisionShape2D ScannerArea;
	private KinematicCollision2D playerShipCollision;

	public PlayerShipStats shipStats { get; private set; } = new();
	private readonly PlayerShipAttr shipAttr = new();
	private readonly PlayerShipConfig shipConfig = new();

	protected internal bool isSetLandingMode = false;
	protected internal bool isAccelerating = false;
	protected internal bool isTurningLeft = false;
	protected internal bool isTurningRight = false;
	protected internal bool isDecelerating = false;
	protected internal bool isAlternateControlHeld = false;
	protected internal bool isChangingFlightMode = false;
	protected internal bool isEngagingAfterburner = false;
	protected internal bool isShooting = false;

	public override void _Ready() // Generate Stats & Skills on Instantiation, 
	{
		// Setup Ship Components
		// Hull
		hull.playerShip = this;
		hull.cB = GetNode<CollisionPolygon2D>("HullCB");
		hull.animPlayer = GetNode<AnimationPlayer>("HAnimPlayer");
		hull.animPlayer.Play("Idle");

		// Engines
		engines.playerShip = this;
		engines.e1flame = GetNode<GpuParticles2D>("Engine1Flame");
		engines.e2flame = GetNode<GpuParticles2D>("Engine2Flame");
		engines.e1trail = GetNode<GpuParticles2D>("Engine1Trail");
		engines.e2trail = GetNode<GpuParticles2D>("Engine2Trail");
		engines.engineFlames = new List<GpuParticles2D> { engines.e1flame, engines.e2flame };
		engines.engineTrails = new List<GpuParticles2D> { engines.e1trail, engines.e2trail };
		engines.e1cB = GetNode<CollisionPolygon2D>("Engine1CB");
		engines.e2cB = GetNode<CollisionPolygon2D>("Engine2CB");
		engines.ChangeFixedState();
		engines.SetIdle();

		// Landing Gear
		landingGear.playerShip = this;
		landingGear.animPlayer = GetNode<AnimationPlayer>("LGAnimPlayer");
		landingGear.cB1 = GetNode<CollisionPolygon2D>("LGCB1");
		landingGear.cB2 = GetNode<CollisionPolygon2D>("LGCB2");
		landingGear.animPlayer.Play("Idle");

		// Scanner
		Scanner = GetNode<Area2D>("Scanner");
		ScannerArea = GetNode<CollisionShape2D>("Scanner/ScannerArea");

		//utilArm.inv = inventory; - REINSERT AFTER CREATING UTILARM & SCENE

		// Setup Ship Config
		shipStats.CurrentFuel.Change(Fuels.Type.Hydrazine);
		shipStats.CurrentFuel.Add(100.0f, shipStats.MaxFuel);
		shipStats.CurrentSuperFuel.Change(SuperFuels.Type.LH2LOX);
		shipStats.CurrentSuperFuel.Add(100.0f, shipStats.MaxSuperFuel);
		flightMode = PlayerShipFlightMode.Combat; // TODO - REMOVE AFTER TESTING

		// Setup Ship Stats and Start Anims
		EmitSignal(SignalName.StatsMaxUpdate, shipStats.Integrity, shipStats.Shield, shipStats.CurrentFuel.Amount, shipStats.CurrentSuperFuel.Amount, shipStats.ElectricCharge, Velocity.Length()); // Stats Max Update Signal
		EmitSignal(SignalName.StatsUpdate, shipStats.Integrity); // Stats Update Signal
		EmitSignal(SignalName.FlightModeUpdate, (int)flightMode); // Flight Mode Update Signal
		EquipWeapon(PlayerWeaponFactory.Type.Blaster);
	}

	public override void _PhysicsProcess(double delta)
	{
		UpdateFlags();
		mousePosition = GetGlobalMousePosition();
		switch (flightMode)
		{
			case PlayerShipFlightMode.Combat:
				checkCombatInput();
				shipHeadingCombat(delta);
				shipMovementCombat(delta);
				break;
			case PlayerShipFlightMode.Utility:
				checkUtilityInput();
				shipHeadingUtility(delta);
				shipMovementUtility(delta);
				break;
			case PlayerShipFlightMode.Landing:
				checkLandingInput();
				shipHeadingLanding(delta);
				shipMovementLanding(delta);
				break;
		}
	}

	public override void _Process(double delta)
	{
		updateCrosshair(mousePosition);
		EmitSignal(SignalName.GridRefUpdate, GridCoords);
	}

	private void UpdateFlags()
	{
		if (shipStats.CurrentFuel.Amount <= 0.0f) { isAccelerating = false; isDecelerating = false; }
		else { isAccelerating = IsUpPressed(); isDecelerating = IsDownPressed(); }
		isTurningLeft = IsLeftPressed();
		isTurningRight = IsRightPressed();
		isSetLandingMode = IsLPressed();
		if (shipStats.CurrentSuperFuel.Amount <= 0.0f) { isEngagingAfterburner = false; }
		else { isEngagingAfterburner = IsCtrlPressed(); }
		isAlternateControlHeld = IsShiftPressed();
		isChangingFlightMode = IsFPressed();
		isShooting = IsSpacePressed();
	}

	private bool IsUpPressed() { return Input.IsPhysicalKeyPressed(Key.W) || Input.IsPhysicalKeyPressed(Key.Up); }
	private bool IsDownPressed() { return Input.IsPhysicalKeyPressed(Key.S) || Input.IsPhysicalKeyPressed(Key.Down); }
	private bool IsLeftPressed() { return Input.IsPhysicalKeyPressed(Key.A) || Input.IsPhysicalKeyPressed(Key.Left); }
	private bool IsRightPressed() { return Input.IsPhysicalKeyPressed(Key.D) || Input.IsPhysicalKeyPressed(Key.Right); }
	private bool IsShiftPressed() { return Input.IsPhysicalKeyPressed(Key.Shift); }
	private bool IsCtrlPressed() { return Input.IsActionJustReleased("ui_afterburner"); }
	private bool IsFPressed() { return Input.IsActionJustReleased("ui_flightmode"); }
	private bool IsLPressed() { return Input.IsActionJustReleased("ui_landing"); }
	private bool IsSpacePressed() { return Input.IsActionJustReleased("ui_shoot"); }

	private void checkCombatInput()
	{
		if (isShooting) { Weapon.Shoot(Velocity); }
		if (isEngagingAfterburner) { engines.ChangeFixedState(); }
		if (isSetLandingMode) { ChangeFlightMode(isSetLandingMode); }
		else
		if (isChangingFlightMode) { ChangeFlightMode(); }
	}

	private void checkUtilityInput()
	{
		if (isAlternateControlHeld && isChangingFlightMode) { hull.ChangeState(); }
		else
		if (isSetLandingMode) { ChangeFlightMode(isSetLandingMode); }
		else
		if (isChangingFlightMode) { ChangeFlightMode(); }

	}

	private void checkLandingInput()
	{
		if (isChangingFlightMode) { ChangeFlightMode(); }
	}

	private void updateCrosshair(Vector2 mousePostion)
	{
		var angleDifference = GetAngleTo(mousePostion);
		var clampedAngle = Rotation + Mathf.Clamp(angleDifference, -Mathf.DegToRad(15), +Mathf.DegToRad(15));
		direction = Vector2.FromAngle(clampedAngle);        // Convert the angle to a unit vector
		Crosshair.Position = Position + direction * shipConfig.CrosshairDistance;       // Move the crosshair towards the direction
	}

	private void shipHeadingCombat(double delta)
	{
		var headingDifference = GetAngleTo(mousePosition);
		if (Mathf.Abs(headingDifference) > (float)0.01)
		{
			Rotate(headingDifference * (float)delta * shipAttr.Agility);
		}
	}

	private void shipMovementCombat(double delta)
	{
		direction = Vector2.FromAngle(Rotation);
		if (isAccelerating && engines.fixedState == PlayerEngines.FixedState.Afterburner)
		{
			var superFuelBurn = shipStats.CurrentSuperFuel.Burn((float)delta);
			if (superFuelBurn)
			{
				engines.ChangeLiveState();
				Velocity += direction * ((shipStats.CurrentFuel.Acceleration + shipStats.CurrentSuperFuel.Acceleration) * (float)delta);
				Velocity = Velocity.LimitLength(shipStats.CurrentFuel.MaxSpeed + shipStats.CurrentSuperFuel.MaxSpeed);
			}
			else
			{
				engines.ChangeFixedState();
				IdleMovement(delta);
			}
		}
		else
		if (isAccelerating)
		{
			shipStats.CurrentFuel.Burn((float)delta);
			engines.ChangeLiveState();
			Velocity += direction * (shipStats.CurrentFuel.Acceleration * (float)delta);
			Velocity = Velocity.LimitLength(shipStats.CurrentFuel.MaxSpeed);
		}
		else
		{
			IdleMovement(delta);
		}
		MoveAndCollide(Velocity * (float)delta);
		EmitSignal(SignalName.StatsUpdate, shipStats.Integrity, shipStats.Shield, shipStats.CurrentFuel.Amount, shipStats.CurrentSuperFuel.Amount, shipStats.ElectricCharge, Velocity.Length());
	}


	private void shipHeadingUtility(double delta)
	{
		if (isTurningLeft) { Rotate(-shipAttr.Agility * (float)delta); }
		if (isTurningRight) { Rotate(shipAttr.Agility * (float)delta); }
	}

	private void shipMovementUtility(double delta)
	{
		direction = Vector2.FromAngle(Rotation);
		if (isAccelerating)
		{
			shipStats.CurrentFuel.Burn((float)delta);
			engines.ChangeLiveState();
			Velocity += direction * (float)(shipStats.CurrentFuel.Acceleration * delta);
			Velocity = Velocity.LimitLength(shipStats.CurrentFuel.MaxSpeed);
		}
		else
		{
			IdleMovement(delta);
		}
		MoveAndCollide(Velocity * (float)delta);
		EmitSignal(SignalName.StatsUpdate, shipStats.Integrity, shipStats.Shield, shipStats.CurrentFuel.Amount, shipStats.CurrentSuperFuel.Amount, shipStats.ElectricCharge, Velocity.Length());
	}

	private void shipHeadingLanding(double delta)
	{
		if (isAlternateControlHeld && isTurningLeft) { Rotate(-shipAttr.LandingAgility * (float)delta); }
		if (isAlternateControlHeld && isTurningRight) { Rotate(shipAttr.LandingAgility * (float)delta); }
	}

	private void shipMovementLanding(double delta)
	{
		direction = Vector2.FromAngle(Rotation);
		var strafeDirection = new Vector2(direction.Y, -direction.X);
		if (isAccelerating)
		{
			shipStats.CurrentFuel.Burn((float)delta);
			Velocity += direction * (float)(shipStats.CurrentFuel.Acceleration * delta);
		}
		else if (isDecelerating)
		{
			shipStats.CurrentFuel.Burn((float)delta);
			Velocity -= direction * (float)(shipStats.CurrentFuel.Acceleration * delta);
		}
		else if (!isAlternateControlHeld && isTurningLeft)
		{
			shipStats.CurrentFuel.Burn((float)delta);
			Velocity += strafeDirection * (float)(shipStats.CurrentFuel.Acceleration * delta);
		}
		else if (!isAlternateControlHeld && isTurningRight)
		{
			shipStats.CurrentFuel.Burn((float)delta);
			Velocity -= strafeDirection * (float)(shipStats.CurrentFuel.Acceleration * delta);
		}
		else
		{
			IdleMovement(delta);
		}
		Velocity = Velocity.LimitLength(shipStats.CurrentFuel.MaxSpeed);
		playerShipCollision = MoveAndCollide(Velocity * (float)delta); // LANDING COLLISION INFORMATION
		if (playerShipCollision != null)
		{
			var hitinfo = playerShipCollision.GetCollider();
			var localShape = playerShipCollision.GetLocalShape();
			GD.Print(" Local Shape: ", localShape.ToString());
		}
		EmitSignal(SignalName.StatsUpdate, shipStats.Integrity, shipStats.Shield, shipStats.CurrentFuel.Amount, shipStats.CurrentSuperFuel.Amount, shipStats.ElectricCharge, Velocity.Length());
	}

	private void IdleMovement(double delta)
	{
		if (Velocity.Length() > (shipAttr.Friction * delta))
		{
			Velocity *= (float)Mathf.Pow(1.0 - shipAttr.Friction, delta);
		}
		else
		{
			Velocity = Vector2.Zero;
		}
		engines.ChangeLiveState();
	}

	private void ChangeFlightMode()
	{
		switch (flightMode)
		{
			case PlayerShipFlightMode.Combat:
				if (isSetLandingMode)
				{
					flightMode = PlayerShipFlightMode.Landing;
					engines.ChangeFixedState();
					landingGear.ChangeFixedState();
					Crosshair.Visible = false;
				}
				else
				{
					flightMode = PlayerShipFlightMode.Utility;
					engines.ChangeFixedState();
					Crosshair.Visible = false;
				}
				break;
			case PlayerShipFlightMode.Utility:
				if (isSetLandingMode)
				{
					flightMode = PlayerShipFlightMode.Landing;
					engines.ChangeFixedState();
					landingGear.ChangeFixedState();
					Crosshair.Visible = false;
				}
				else
				{
					flightMode = PlayerShipFlightMode.Combat;
					engines.ChangeFixedState();
					Crosshair.Visible = true;
				}
				break;
			case PlayerShipFlightMode.Landing:
				flightMode = PlayerShipFlightMode.Utility;
				engines.ChangeFixedState();
				landingGear.ChangeFixedState();
				Crosshair.Visible = false;
				break;
			default:
				GD.PrintErr("Unexpected flight mode: " + flightMode);
				break;
		}
		EmitSignal(SignalName.FlightModeUpdate, (int)flightMode);
	}

	private void ChangeFlightMode(bool isSetLandingMode = false)
	{
		if (isSetLandingMode)
		{
			if (flightMode != PlayerShipFlightMode.Landing)
			{
				flightMode = PlayerShipFlightMode.Landing;
				engines.ChangeFixedState();
				landingGear.ChangeFixedState();
				Crosshair.Visible = false;
			}
		}
		else
			switch (flightMode)
			{
				case PlayerShipFlightMode.Landing:
					flightMode = PlayerShipFlightMode.Combat;
					engines.ChangeFixedState();
					landingGear.ChangeFixedState();
					Crosshair.Visible = true;
					break;
				case PlayerShipFlightMode.Utility:
					flightMode = PlayerShipFlightMode.Combat;
					engines.ChangeFixedState();
					Crosshair.Visible = true;
					break;
				case PlayerShipFlightMode.Combat:
					flightMode = PlayerShipFlightMode.Utility;
					engines.ChangeFixedState();
					Crosshair.Visible = false;
					break;
			};
		EmitSignal(SignalName.FlightModeUpdate, (int)flightMode);
	}

	private void EquipWeapon(PlayerWeaponFactory.Type weaponType)
	{
		Weapon?.QueueFree();
		Weapon = PlayerWeaponFactory.LoadWeapon(weaponType);
		weaponSlot = GetNode<Node2D>("WeaponSlot");
		weaponSlot.AddChild(Weapon);
		EmitSignal(SignalName.WeaponUpdate, (int)weaponType);
		Weapon.OnEquip();
	}
}