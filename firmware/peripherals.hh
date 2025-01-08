/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_PERIPHERALS_HH)
#define SQUISHY_SUPERVISOR_PERIPHERALS_HH

#include <cstdint>
#include <cstddef>
#include <array>

/* ==== SAMD09 Peripherals ==== */

/* Power Manager */

constexpr static std::uintptr_t PM_BASE{0x40000400U};

struct pm_t final {
	enum struct ahb_periph_t : std::uint8_t {
		HPB0     = 0x00U,
		HPB1     = 0x01U,
		HPB2     = 0x02U,
		DSU      = 0x03U,
		NVMCTRL = 0x04U,
		DMAC     = 0x05U,
	};
	enum struct apba_periph_t : std::uint8_t {
		PAC0    = 0x00U,
		PM      = 0x01U,
		SYSCTRL = 0x02U,
		GCLK    = 0x03U,
		WDT     = 0x04U,
		RTC     = 0x05U,
		EIC     = 0x06U,
	};
	enum struct apbb_periph_t : std::uint8_t {
		PAC1    = 0x00U,
		DSU     = 0x01U,
		NVMCTRL = 0x02U,
		PORT    = 0x03U,
		DMAC    = 0x04U,
	};
	enum struct apbc_periph_t : std::uint8_t {
		PAC2    = 0x00U,
		EVSYS   = 0x01U,
		SERCOM0 = 0x02U,
		SERCOM1 = 0x03U,
		TC1     = 0x06U,
		TC2     = 0x07U,
		ADC     = 0x08U
	};

	volatile std::uint8_t ctrl;
	volatile std::uint8_t sleep;
	volatile std::uint8_t extctrl;
	const std::array<std::uint8_t, 5> _reserved0;
	volatile std::uint8_t cpusel;
	volatile std::uint8_t apbasel;
	volatile std::uint8_t apbbsel;
	volatile std::uint8_t apbcsel;
	const std::array<std::uint8_t, 8> _reserved1;
	volatile std::uint32_t ahbmask;
	volatile std::uint32_t apbamask;
	volatile std::uint32_t apbbmask;
	volatile std::uint32_t apbcmask;
	const std::array<std::uint8_t, 15> _reserved2;
	volatile std::uint8_t intenclr;
	volatile std::uint8_t intenset;
	volatile std::uint8_t intflag;
	volatile std::uint8_t reserved3;
	volatile std::uint8_t rcause;

	void unmask(ahb_periph_t periph) noexcept {
		ahbmask = (
			ahbmask | (1U << static_cast<std::uint8_t>(periph))
		);
	}

	void unmask(apba_periph_t periph) noexcept {
		apbamask = (
			apbamask | (1U << static_cast<std::uint8_t>(periph))
		);
	}

	void unmask(apbb_periph_t periph) noexcept {
		apbbmask = (
			apbbmask | (1U << static_cast<std::uint8_t>(periph))
		);
	}

	void unmask(apbc_periph_t periph) noexcept {
		apbcmask = (
			apbcmask | (1U << static_cast<std::uint8_t>(periph))
		);
	}

	bool was_por() noexcept {
		return (rcause & 0x01U);
	}

	bool was_brownout() noexcept {
		return (rcause & 0x06U);
	}
};

inline auto& PM{*reinterpret_cast<pm_t*>(PM_BASE)};

/* System Controller */

constexpr static std::uintptr_t SYSCTRL_BASE{0x40000800U};

struct sysctrl_t final {
	volatile std::uint32_t intencrl;
	volatile std::uint32_t intenset;
	volatile std::uint32_t intflag;
	volatile std::uint32_t pclksr;
	volatile std::uint16_t xosc;
	const std::uint16_t _reserved0;
	volatile std::uint16_t xosc32k;
	const std::uint16_t _reserved1;
	volatile std::uint32_t osc32k;
	volatile std::uint8_t osculp32k;
	const std::array<const std::uint8_t, 3> _reserved2;
	volatile std::uint32_t osc8m;
	volatile std::uint16_t dfllctrl;
	const std::uint16_t _reserved3;
	volatile std::uint32_t dfllval;
	volatile std::uint32_t dfllmul;
	volatile std::uint8_t dfllsync;
	const std::array<const std::uint8_t, 3> _reserved4;
	volatile std::uint32_t bod33;
	const std::array<const std::uint32_t, 2> _reserved5;
	volatile std::uint32_t vref;
	volatile std::uint8_t dpllctrla;
	const std::array<const std::uint8_t, 3> _reserved6;
	volatile std::uint32_t dpllratio;
	volatile std::uint32_t dpllctrlb;
	volatile std::uint8_t dpllstatus;
	const std::array<const std::uint8_t, 3> _reserved7;


	void enable_bod33(std::uint8_t level) noexcept {
		bod33 = (1U << 1U) | (1U << 3U) | (1U << 6U) | ((level & 0x3FU) << 16U);
	}
};

inline auto& SYSCTRL{*reinterpret_cast<sysctrl_t*>(SYSCTRL_BASE)};

/* GCLK */

constexpr static std::uintptr_t GCLK_BASE{0x40000C00U};

struct gclk_t final {

	enum struct clkgen_t : std::uint8_t {
		GCLK0 = 0x00U,
		GCLK1 = 0x01U,
		GCLK2 = 0x02U,
		GCLK3 = 0x03U,
		GCLK4 = 0x04U,
		GCLK5 = 0x05U,
	};

	enum struct clkid_t : std::uint8_t {
		DFLL48M_REF  = 0x00U,
		DPLL         = 0x01U,
		DPLL32K      = 0x02U,
		WDT          = 0x03U,
		RTC          = 0x04U,
		EIC          = 0x05U,
		EVSYS_CHAN0  = 0x07U,
		EVSYS_CHAN1  = 0x08U,
		EVSYS_CHAN2  = 0x09U,
		EVSYS_CHAN3  = 0x0AU,
		EVSYS_CHAN4  = 0x0BU,
		EVSYS_CHAN5  = 0x0CU,
		SERCOMx_SLOW = 0x0DU,
		SERCOM0_CORE = 0x0EU,
		SERCOM1_CORE = 0x0FU,
		TC2          = 0x012U,
		ADC          = 0x013U,
	};

	enum struct clksrc_t : std::uint8_t {
		XOSC      = 0x00U,
		GCLKIN    = 0x01U,
		GCLKGEN1  = 0x02U,
		OSCULP32K = 0x03U,
		OSC32K    = 0x04U,
		XOSC32K   = 0x05U,
		OSC8M     = 0x06U,
		DFLL48M   = 0x07U,
		FDPLL96M  = 0x08U,
	};

	volatile std::uint8_t ctrl;
	volatile std::uint8_t status;
	volatile std::uint16_t clkctrl;
	volatile std::uint32_t genctrl;
	volatile std::uint32_t gendiv;

	bool sync_busy() noexcept {
		return (status & 0x40U) >> 6U;
	}

	void config_clk(clkid_t id, clkgen_t gen, bool enabled, bool lock) noexcept {
		clkctrl = std::uint16_t(
			static_cast<std::uint8_t>(id)               |
			(static_cast<std::uint8_t>(gen)     <<  8U) |
			(static_cast<std::uint8_t>(enabled) << 14U) |
			(static_cast<std::uint8_t>(lock)    << 15U)
		);
	}

	void config_gen(clkgen_t gen, clksrc_t src, bool enabled) noexcept {
		genctrl = std::uint32_t(
			static_cast<std::uint8_t>(gen)              |
			(static_cast<std::uint8_t>(src)     <<  8U) |
			(static_cast<std::uint8_t>(enabled) << 16U)
		);
	}
};

inline auto& GCLK{*reinterpret_cast<gclk_t*>(GCLK_BASE)};

/* Watchdog */

constexpr static std::uintptr_t WDT_BASE{0x40001000U};

struct wdt_t final {
	/* TODO */

};

inline auto& WDT{*reinterpret_cast<wdt_t*>(WDT_BASE)};

/* RTC */

constexpr static std::uintptr_t RTC_BASE{0x40001400U};

struct rtc_t final {
	/* TODO */
};

inline auto& RTC{*reinterpret_cast<rtc_t*>(RTC_BASE)};

/* EIC */

constexpr static std::uintptr_t EIC_BASE{0x40001800U};

struct eic_t final {
	enum struct sense_t : std::uint8_t {
		NONE = 0x00U,
		RISE = 0x01U,
		FALL = 0x02U,
		BOTH = 0x03U,
		HIGH = 0x04U,
		LOW  = 0x05U,
	};

	volatile std::uint8_t ctrl;
	volatile std::uint8_t status;
	volatile std::uint8_t nmictrl;
	volatile std::uint8_t nmiflag;
	volatile std::uint32_t evctrl;
	volatile std::uint32_t intenclr;
	volatile std::uint32_t intenset;
	volatile std::uint32_t intflag;
	volatile std::uint32_t wakeup;
	volatile std::uint32_t config;

	void enable() noexcept {
		ctrl |= (1U << 1U);
		while (syncbusy()) {
			continue;
		}
	}

	void disable() noexcept {
		ctrl &= static_cast<std::uint8_t>(~(1U << 1U));
		while (syncbusy()) {
			continue;
		}
	}

	[[nodiscard]]
	bool syncbusy() noexcept {
		return (status & 0x80) >> 7U;
	}

	void enable_extint_irq(const std::uint8_t extint) noexcept {
		intenset = (1U << extint);
	}

	void disable_extint_irq(const std::uint8_t extint) noexcept {
		intenclr = (1U << extint);
	}

	std::uint8_t get_extint_irq() noexcept {
		return static_cast<std::uint8_t>(intflag);
	}

	void ack_extint(const std::uint8_t extint) noexcept {
		intflag = (1U << extint);
	}

	void enable_extint(const std::uint8_t extint, const bool filt_en, const sense_t sense) noexcept {
		config |= (std::uint32_t{
			(static_cast<std::uint32_t>(filt_en) << 3U) | static_cast<std::uint8_t>(sense)
		} << (extint * 4U));
	}

	void disable_extint(const std::uint8_t extint) noexcept {
		config &= ~(0x0FU << (extint * 4U));
	}
};

inline auto& EIC{*reinterpret_cast<eic_t*>(EIC_BASE)};

/* Device Service Unit */

constexpr static std::uintptr_t DSU_BASE{0x41002000U};

struct dsu_t final {
	volatile std::uint8_t ctrl;
	volatile std::uint8_t statusa;
	volatile std::uint8_t statusb;
	const std::uint8_t _reserved0;

	void reset_core() noexcept {
		ctrl |= 0x01U;
	}
};

inline auto& DSU{*reinterpret_cast<dsu_t*>(DSU_BASE)};

/* NVMCTRL */

constexpr static std::uintptr_t NVMCTRL_BASE{0x41004000U};

struct nvmctrl_t final {
	/* TODO */
};

inline auto& NVMCTRL{*reinterpret_cast<nvmctrl_t*>(NVMCTRL_BASE)};

/* Ports */

constexpr static std::uintptr_t PORTA_BASE{0x41004400U};
constexpr static std::uintptr_t PORTB_BASE{0x41004480U};

struct port_t final {
	enum struct pin_func_t : std::uint8_t {
		A = 0x00U,
		B = 0x01U,
		C = 0x02U,
		D = 0x03U,
		E = 0x04U,
		F = 0x05U,
		G = 0x06U,
		H = 0x07U,
	};

	volatile std::uint32_t dir;
	volatile std::uint32_t dirclr;
	volatile std::uint32_t dirset;
	volatile std::uint32_t dirtgl;
	volatile std::uint32_t out;
	volatile std::uint32_t outclr;
	volatile std::uint32_t outset;
	volatile std::uint32_t outtgl;
	volatile std::uint32_t in;
	volatile std::uint32_t ctrl;
	volatile std::uint32_t wrconfig;
	const std::uint32_t reserved1;
	std::array<volatile std::uint8_t, 16> pmux;
	std::array<volatile std::uint8_t, 32> pcfg;

	void set_input(const std::uint8_t pin) noexcept {
		dirclr = 1U << pin;
	}

	void set_output(const std::uint8_t pin) noexcept {
		dirset = 1U << pin;
	}

	void toggle_dir(const std::uint8_t pin) noexcept {
		dirtgl = 1U << pin;
	}

	void set_low(const std::uint8_t pin) noexcept {
		outclr = 1U << pin;
	}

	void set_high(const std::uint8_t pin) noexcept {
		outset = 1U << pin;
	}

	void set_value(const bool state, const std::uint8_t pin) noexcept {
		(state ? outset : outclr) = 1U << pin;
	}

	void toggle(const std::uint8_t pin) noexcept {
		outtgl = 1U << pin;
	}

	[[nodiscard]]
	bool pin_state(const std::uint8_t pin) noexcept {
		return (in & std::uint32_t(1U << pin));
	}

	void pin_config(const std::uint8_t pin, bool pmux_en, bool in_en, bool pull_en, bool strong_drive) noexcept {
		auto& pin_cfg{pcfg.at(pin)};
		pin_cfg = std::uint8_t(
			(static_cast<std::uint8_t>(pmux_en)      << 0U) |
			(static_cast<std::uint8_t>(in_en)        << 1U) |
			(static_cast<std::uint8_t>(pull_en)      << 2U) |
			(static_cast<std::uint8_t>(strong_drive) << 6U)
		);
	}

	void pin_function(const std::uint8_t pin, pin_func_t func) noexcept {
		auto& pin_mux{pmux.at(pin >> 1U)};
		const auto pmux_shift{(pin & 1U) << 2U};
		auto mux_cfg{pin_mux & ~(0xFU << (pmux_shift))};
		mux_cfg |= (static_cast<std::uint8_t>(func) & 0xFU) << pmux_shift;
		pin_mux = std::uint8_t(mux_cfg);
	}


	[[nodiscard]]
	pin_func_t pin_function(const std::uint8_t pin) noexcept {
		auto& pin_mux{pmux.at(pin >> 1U)};
		const auto pmux_shift{(pin & 1U) << 2U};
		const auto mux_cfg{pin_mux & ~(0xFU << (pmux_shift))};
		return static_cast<pin_func_t>(mux_cfg >> pmux_shift);
	}

	void setup_pin(
		const std::uint8_t pin, bool pmux_en, bool in_en, bool pull_en,
		bool strong_drive, pin_func_t func
	) noexcept {
		pin_function(pin, func);
		pin_config(pin, pmux_en, in_en, pull_en, strong_drive);
	}
};

inline auto& PORTA{*reinterpret_cast<port_t*>(PORTA_BASE)};
inline auto& PORTB{*reinterpret_cast<port_t*>(PORTB_BASE)};

/* DMAC */

constexpr static std::uintptr_t DMAC_BASE{0x41004800U};

struct dmac_t final {
	/* TODO */
};

inline auto& DMAC{*reinterpret_cast<dmac_t*>(DMAC_BASE)};

/* MTB */

constexpr static std::uintptr_t MTB_BASE{0x41006000U};

struct mtb_t final {
	/* TODO */
};

inline auto& MTB{*reinterpret_cast<mtb_t*>(MTB_BASE)};

/* Event System */

constexpr static std::uintptr_t EVSYS_BASE{0x42000400U};

struct evsys_t final {
	/* TODO */
};

inline auto& EVSYS{*reinterpret_cast<evsys_t*>(EVSYS_BASE)};

/* SERCOM */

constexpr static std::uintptr_t SERCOM0_BASE{0x42000800U};
constexpr static std::uintptr_t SERCOM1_BASE{0x42000C00U};

struct sercom_usart_t final {
	/* TODO */
};

struct sercom_i2c_t final {
	/* TODO */
};

struct sercom_spi_t final {
	enum struct mode_t : std::uint8_t {
		Perphieral = 0x02U,
		Controller = 0x03U,
	};

	enum struct dopo_t : std::uint8_t {
		CFG0 = 0x00U, /* PAD0 = COPI; PAD1 = CLK; PAD2 = CS */
		CFG1 = 0x01U, /* PAD2 = COPI; PAD3 = CLK; PAD1 = CS */
		CFG2 = 0x02U, /* PAD3 = COPI; PAD1 = CLK; PAD2 = CS */
		CFG3 = 0x03U, /* PAD0 = COPI; PAD3 = CLK; PAD1 = CS */
	};

	enum struct dipo_t : std::uint8_t {
		PAD0 = 0x00U,
		PAD1 = 0x01U,
		PAD2 = 0x02U,
		PAD3 = 0x03U,
	};

	enum struct form_t : std::uint8_t {
		SPI      = 0x00U,
		SPI_ADDR = 0x02U,
	};

	enum struct cpha_t : std::uint8_t {
		SAMPLE_LEADING  = 0x00U,
		SAMPLE_TRAILING = 0x01U,
	};

	enum struct cpol_t : std::uint8_t {
		IDLE_LOW  = 0x00U,
		IDLE_HIGH = 0x01U,
	};

	enum struct dord_t : std::uint8_t {
		MSB = 0x00U,
		LSB = 0x01U,
	};

	enum struct chsize_t : std::uint8_t {
		EIGHT = 0x00U,
		NINE  = 0x01U,
	};

	volatile std::uint32_t ctrla;
	volatile std::uint32_t ctrlb;
	const std::array<const std::uint8_t, 4> reserved0;
	volatile std::uint8_t baud;
	const std::array<const std::uint8_t, 7> reserved1;
	volatile std::uint8_t intenclr;
	const std::uint8_t reserved2;
	volatile std::uint8_t intenset;
	const std::uint8_t reserved3;
	volatile std::uint8_t intflag;
	const std::uint8_t reserved4;
	volatile std::uint16_t status;
	volatile std::uint32_t syncbusy;
	const std::array<const std::uint8_t, 4> reserved5;
	volatile std::uint32_t addr;
	volatile std::uint16_t data;
	const std::array<const std::uint8_t, 6> reserved6;
	volatile std::uint8_t dbgctrl;
	const std::array<const std::uint8_t, 3> paddin0;

	void enable() noexcept {
		ctrla |= (1U << 1U);
		while (sync_busy_ctrla()) {
			continue;
		}
	}

	void disable() noexcept {
		ctrla &= ~(1U << 1U);
		while (sync_busy_ctrla()) {
			continue;
		}
	}

	[[nodiscard]]
	bool enabled() noexcept {
		return (ctrla & (1U << 1U));
	}

	[[nodiscard]]
	bool sync_busy_ctrla() noexcept {
		return (syncbusy & (1U << 1U));
	}

	[[nodiscard]]
	bool sync_busy_ctrlb() noexcept {
		return (syncbusy & (1U << 2U));
	}

	[[nodiscard]]
	bool data_empty() noexcept {
		return (intflag & (1U << 0U));
	}

	[[nodiscard]]
	bool receive_complete() noexcept {
		return (intflag & (1U << 2U));
	}

	void configure(
		mode_t mode,
		dopo_t dopo, dipo_t dipo, form_t form,
		cpha_t cpha, cpol_t cpol,
		dord_t dord,
		bool ibon = false
	) noexcept {
		ctrla = std::uint32_t(
			(static_cast<std::uint8_t>(mode) <<  2U) |
			(static_cast<std::uint8_t>(ibon) <<  8U) |
			(static_cast<std::uint8_t>(dopo) << 16U) |
			(static_cast<std::uint8_t>(dipo) << 20U) |
			(static_cast<std::uint8_t>(form) << 24U) |
			(static_cast<std::uint8_t>(cpha) << 28U) |
			(static_cast<std::uint8_t>(cpol) << 29U) |
			(static_cast<std::uint8_t>(dord) << 30U)
		);
	}
};

inline auto& SERCOM0_USART{*reinterpret_cast<sercom_usart_t*>(SERCOM0_BASE)};
inline auto& SERCOM1_USART{*reinterpret_cast<sercom_usart_t*>(SERCOM1_BASE)};

inline auto& SERCOM0_I2C{*reinterpret_cast<sercom_i2c_t*>(SERCOM0_BASE)};
inline auto& SERCOM1_I2C{*reinterpret_cast<sercom_i2c_t*>(SERCOM1_BASE)};

inline auto& SERCOM0_SPI{*reinterpret_cast<sercom_spi_t*>(SERCOM0_BASE)};
inline auto& SERCOM1_SPI{*reinterpret_cast<sercom_spi_t*>(SERCOM1_BASE)};


/* Timers/Counters */

constexpr static std::uintptr_t TIC1_BASE{0x42001800U};
constexpr static std::uintptr_t TIC2_BASE{0x42001C00U};

struct tic_t final {
	/* TODO */
};

inline auto& TIC1{*reinterpret_cast<tic_t*>(TIC1_BASE)};
inline auto& TIC2{*reinterpret_cast<tic_t*>(TIC2_BASE)};

/* ADC */

constexpr static std::uintptr_t ADC_BASE{0x42002000U};

struct adc_t final {
	/* TODO */
};

inline auto& ADC{*reinterpret_cast<adc_t*>(ADC_BASE)};

/* ==== ARM Peripherals ==== */

constexpr static std::uintptr_t SYSTICK_BASE{0xE000E010U};

struct systick_t final {
	volatile std::uint32_t ctrl_status;
	volatile std::uint32_t reload_value;
	volatile std::uint32_t current_value;
	volatile const std::uint32_t calibration_value;

	void enable() noexcept {
		ctrl_status |= (1U << 0U) | (1U << 1U) | (1U << 2U);
	}
};

inline auto& SYSTICK{*reinterpret_cast<systick_t*>(SYSTICK_BASE)};

constexpr static std::uintptr_t NVIC_BASE{0xE000E100U};

struct nvic_t final {
	enum struct priority_t : std::uint8_t {
		TOP = 0x00U,

		LOW = 0x3FU,
	};

	volatile std::uint32_t itrseten;
	const std::array<const std::uint32_t, 31> _reserved0;
	volatile std::uint32_t itrclren;
	const std::array<const std::uint32_t, 31> _reserved1;
	volatile std::uint32_t itrsetpend;
	const std::array<const std::uint32_t, 31> _reserved2;
	volatile std::uint32_t itrclrpend;
	const std::array<const std::uint32_t, 31> _reserved3;
	std::array<volatile std::uint32_t, 8> itrpriority;


	void set_priority(std::uint8_t interrupt_number, priority_t priority) noexcept {
		const auto reg_num{std::uint8_t(interrupt_number >> 2U)};
		const auto pri_idx{std::uint8_t(interrupt_number & 0x3U)};

		auto& reg{itrpriority.at(reg_num)};

		/* Clear old priority */
		reg &= ~std::uint32_t(static_cast<std::uint8_t>(priority_t::LOW) << (pri_idx * 8U));
		/* Set new priority */
		reg |= std::uint32_t(static_cast<std::uint8_t>(priority) << (pri_idx * 8U));
	}
};

inline auto& NVIC{*reinterpret_cast<nvic_t*>(NVIC_BASE)};


#endif /* SQUISHY_SUPERVISOR_PERIPHERALS_HH */
