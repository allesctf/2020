-- DON'T USE PASTEBIN!! IT COULD LEAK THE SOLUTION
-- 1. replace my_ip with your ip
-- 2. start run.sh and make sure it is reachable from outside
--    or opencomputers will crash and you will have to restart the server
-- 3. copy this program to your opencomputers computer e.g. via wget
-- 4. run the lua proxy
-- 5. press a key on the run.sh script to start pyCraft
-- 6. wait until you don't see any new packets + some seconds
-- 7. type /op <Username> to op yourself
-- 8. use the op account and execute /flag to get the flag

local my_ip = "your_python_proxy_ip_here"

local component = require("component")
local internet = component.internet
local keyboard = require("keyboard")
local computer = require("computer")

local running = true

stage = 0

-- lua5.4 has bit op
local bit32 = bit32 or load([[return {
    band = function(a, b) return a & b end,
    bor = function(a, b) return a | b end,
    bxor = function(a, b) return a ~ b end,
    bnot = function(a) return ~a end,
    rshift = function(a, n) return a >> n end,
    lshift = function(a, n) return a << n end,
}]])()

function readVarInt(data)
    local c = 0
    local n = 0
    while true do
        local b = string.byte(data, c + 1)
        n = bit32.bor(n, bit32.lshift(bit32.band(b, 0x7F), 7 * c))
        c = c + 1
        if bit32.band(b, 0x80) == 0 then
            break
        end
    end
    return n, string.sub(data, c), c
end

while running do
    local from = internet.connect(my_ip, 2337)
    local to = internet.connect("0.0.0.0", 31337)

    repeat
        os.sleep(0.01)
    until from.finishConnect()

    repeat
        os.sleep(0.01)
    until to.finishConnect()
    print("Connected!")

    compressed = false
    rem = 0
    buf = ""
    kbuf = ""
    skip = false
    compressed_packet_count = 0
    n_skip_buffering = 20
    function handle(data, src)
        if src == from then
            to.write(data)
        end
        if src == to then
            if stage == 0 then
                from.write(data)
                return
            end
            while data ~= "" and data ~= nil do
                if rem > 0 then
                    length = string.len(data)
                    if rem - length <= 0 then
                        buf = buf .. string.sub(data, 1, rem)
                        if not skip then
                            from.write(buf)
                        end
                        data = string.sub(data, rem + 1)
                        rem = 0
                        buf = ""
                        skip = false
                    else
                        rem = rem - length
                        buf = buf .. data
                        data = ""
                    end
                else
                    length, rest, c = readVarInt(data)
                    id, rest2, c2 = readVarInt(rest)

                    if compressed then
                        rem = length + c - string.len(data)
                        if rem <= 0 then
                            rem = 0
                            if true then
                                kbuf = kbuf .. string.sub(data, 1, c + length)
                            end
                            if string.len(kbuf) > 2048 or n_skip_buffering > 0 then

                                from.write(kbuf)
                                kbuf = ""
                                n_skip_buffering = n_skip_buffering - 1
                            end
                            data = string.sub(data, length + c + 1)
                        else
                            rem = length + c
                            skip = true
                            from.write(kbuf)
                            kbuf = ""
                        end
                        buf = ""
                    else
                        if id == 0x03 and not compressed then
                            print("Now compressed")
                            compressed = true
                        end
                        from.write(string.sub(data, 1, c + length))
                        data = string.sub(data, length + c + 1)
                    end
                end
            end
        end
    end


    local last_recv = computer.uptime()

    while not keyboard.isKeyDown(keyboard.keys.space) do
        if computer.uptime() - last_recv > 10 and stage == 0 then
            print("TIMEOUT")
            print("Login stage :)")
            break
        end

        if compressed then
            compressed_packet_count = compressed_packet_count + 1
        end
        if compressed_packet_count < 10 then
            data = to.read(2048)
            if data == nil then
                print("Closed")
                break
            end
            if data ~= "" then
                handle(data, to)
                from.read(0)
            else

                local data = from.read(2048)

                if data == nil then
                    print("Closed")
                    break
                end

                if data ~= "" then
                    handle(data, from)
                end
            end
        else

            local data = from.read(2048)

            if data == nil then
                print("Closed")
                break
            end

            if data ~= "" then
                handle(data, from)
            end
        end

    end

    if stage == 0 then
        stage = 1
    else
        stage = 0
    end

    from.close()
    to.close()
end
