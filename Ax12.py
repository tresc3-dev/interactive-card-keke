import msvcrt
from dynamixel_sdk import *  # Uses Dynamixel SDK library


def getch():
    return msvcrt.getch().decode()


class Ax12:
    def __init__(self, number):
        # Control table address
        self.ADDR_MX_TORQUE_ENABLE = 24  # Control table address is different in Dynamixel model
        self.ADDR_MX_GOAL_POSITION = 30
        self.ADDR_MX_PRESENT_POSITION = 36

        # Protocol version
        self.PROTOCOL_VERSION = 1.0  # See which protocol version is used in the Dynamixel

        # Default setting
        self.DXL_ID = [i for i in range(number)]  # Dynamixel ID : 1
        self.BAUDRATE = 1000000  # Dynamixel default baudrate : 57600
        self.DEVICENAME = "COM5"  # Check which port is being used on your controller
        # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

        self.TORQUE_ENABLE = 1  # Value for enabling the torque
        self.TORQUE_DISABLE = 0  # Value for disabling the torque
        self.DXL_MINIMUM_POSITION_VALUE = 207  # Dynamixel will rotate between this value
        self.DXL_MAXIMUM_POSITION_VALUE = 828  # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
        self.DXL_MOVING_STATUS_THRESHOLD = 20  # Dynamixel moving status threshold

        self.dxl_goal_position = [
            self.DXL_MINIMUM_POSITION_VALUE,
            512,
            self.DXL_MAXIMUM_POSITION_VALUE,
        ]

        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.portHandler = PortHandler(self.DEVICENAME)

        # Initialize PacketHandler instance
        # Set the protocol version
        # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)

        self.index = 0
        self.is_moving = [False for _ in range(number)]

        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(self.BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()

        # Enable Dynamixel Torque
        for id in self.DXL_ID:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                self.portHandler, id, self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_ENABLE
            )
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            else:
                print("Dynamixel has been successfully connected")

    def ready(self):
        for id in self.DXL_ID:
            self.center(id)

    def move(self, id):
        if self.is_moving[id]:
            return True
        # Write goal position
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler,
            id,
            self.ADDR_MX_GOAL_POSITION,
            self.dxl_goal_position[self.index],
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        self.is_moving[id] = True

    def center(self, id):
        if not self.is_moving[id]:
            return True
        # Write goal position
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler,
            id,
            self.ADDR_MX_GOAL_POSITION,
            self.dxl_goal_position[1],
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        self.is_moving[id] = False

    def set_index(self):
        self.index = 2 if self.index == 0 else 0

    def release(self):
        for id in self.DXL_ID:
            # Disable Dynamixel Torque
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                self.portHandler, id, self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_DISABLE
            )
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        # Close port
        self.portHandler.closePort()


if __name__ == "__main__":
    ax12 = Ax12(1)

    while True:
        if getch() == chr(0x1B):
            break
        ax12.move()

    ax12.release()