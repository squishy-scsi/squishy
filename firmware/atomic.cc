/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>

[[using gnu: always_inline, artificial]]
static inline void pre_barrier(const int) noexcept {
	__atomic_thread_fence(__ATOMIC_SEQ_CST);
}

[[using gnu: always_inline, artificial]]
static inline void post_barrier(const int) noexcept {
	__atomic_thread_fence(__ATOMIC_SEQ_CST);
}


[[using gnu: always_inline, artificial]]
static inline void pre_seq_barrier(const int model) noexcept {
	if (model == __ATOMIC_SEQ_CST) {
		__atomic_thread_fence(model);
	}
}

[[using gnu: always_inline, artificial]]
static inline void post_seq_barrier(const int model) noexcept {
	if (model == __ATOMIC_SEQ_CST) {
		__atomic_thread_fence(model);
	}
}

[[using gnu: always_inline, artificial]]
static inline std::uint32_t protect_begin(const void* const) noexcept {
	std::uint32_t primask{};

	/* Cache if interrupts are enabled or disabled, then disable them */
	asm volatile (R"(
		mrs %0, primask
		cpsid i
	)" : "=r" (primask));

	return primask;
}

[[using gnu: always_inline, artificial]]
static inline void protect_end(const void* const, const std::uint32_t primask) noexcept {
	if (primask == 0U) {
		/* If interrupts were enabled prior, then re-enable them */
		asm volatile ("cpsie i");
	}
}

extern "C" std::uint16_t atomic_fetch_add_2(std::uint16_t* const atomic_value, const std::uint16_t add_value, const int model) noexcept {
	pre_barrier(model);

	auto current_value{*atomic_value};

	std::uint16_t new_value{};

	do {
		new_value = std::uint16_t(current_value + add_value);
	} while (!__atomic_compare_exchange_n(
		atomic_value, &current_value, new_value, 1, __ATOMIC_RELAXED, __ATOMIC_RELAXED
	));


	post_barrier(model);

	return current_value;
}

extern "C" std::uint32_t atomic_fetch_add_4(std::uint32_t* const atomic_value, const std::uint32_t add_value, const int model) noexcept {
	pre_barrier(model);

	auto current_value{*atomic_value};

	std::uint32_t new_value{};

	do {
		new_value = current_value + add_value;
	} while (!__atomic_compare_exchange_n(
		atomic_value, &current_value, new_value, 1, __ATOMIC_RELAXED, __ATOMIC_RELAXED
	));


	post_barrier(model);

	return current_value;
}

extern "C" bool atomic_cmpxchng_1(
	std::uint8_t* const atomic_value, std::uint8_t* const expected_value, const std::uint8_t new_value,
	const bool, const int success_model, const int
) noexcept {

	pre_seq_barrier(success_model);

	const auto prot_state{protect_begin(atomic_value)};

	const auto old_value{*atomic_value};
	const auto res{old_value == *expected_value};

	if (res) {
		*atomic_value = new_value;
	} else {
		*expected_value = old_value;
	}

	protect_end(atomic_value, prot_state);
	post_seq_barrier(success_model);

	return res;
}

extern "C" std::uint8_t atomic_exchange_1(
	std::uint8_t* const atomic_value, const std::uint8_t new_value, const int swap_model
) noexcept {

	pre_seq_barrier(swap_model);

	const auto prot_state{protect_begin(atomic_value)};
	const auto old_value{*atomic_value};

	*atomic_value = new_value;

	protect_end(atomic_value, prot_state);
	post_seq_barrier(swap_model);

	return old_value;
}

extern "C" bool atomic_cmpxchng_2(
	std::uint16_t* const atomic_value, std::uint16_t* const expected_value, const std::uint16_t new_value,
	const bool, const int success_model, const int
) noexcept {

	pre_seq_barrier(success_model);

	const auto prot_state{protect_begin(atomic_value)};

	const auto old_value{*atomic_value};
	const auto res{old_value == *expected_value};

	if (res) {
		*atomic_value = new_value;
	} else {
		*expected_value = old_value;
	}

	protect_end(atomic_value, prot_state);
	post_seq_barrier(success_model);

	return res;
}


extern "C" bool atomic_cmpxchng_4(
	std::uint32_t* const atomic_value, std::uint32_t* const expected_value, const std::uint32_t new_value,
	const bool, const int success_model, const int
) noexcept {

	pre_seq_barrier(success_model);

	const auto prot_state{protect_begin(atomic_value)};

	const auto old_value{*atomic_value};
	const auto res{old_value == *expected_value};

	if (res) {
		*atomic_value = new_value;
	} else {
		*expected_value = old_value;
	}

	protect_end(atomic_value, prot_state);
	post_seq_barrier(success_model);

	return res;
}

extern "C" {
	[[using gnu: alias("atomic_fetch_add_2"), used]]
	unsigned short __atomic_fetch_add_2(volatile void* atomic_value, unsigned short add_value, int swap_model) noexcept;

	[[using gnu: alias("atomic_fetch_add_4"), used]]
	unsigned int __atomic_fetch_add_4(volatile void* atomic_value, unsigned int add_value, int swap_model) noexcept;

	[[using gnu: alias("atomic_exchange_1"), used]]
	unsigned char __atomic_exchange_1(volatile void* atomic_value, unsigned char new_value, int swap_model) noexcept;

	[[using gnu: alias("atomic_cmpxchng_1"), used]]
	bool __atomic_compare_exchange_1(volatile void* atomic_value, void* expected_value, unsigned char new_value, bool weak, int success_model, int failure_model) noexcept;

	[[using gnu: alias("atomic_cmpxchng_2"), used]]
	bool __atomic_compare_exchange_2(volatile void* atomic_value, void* expected_value, unsigned short new_value, bool weak, int success_model, int failure_model) noexcept;

	[[using gnu: alias("atomic_cmpxchng_4"), used]]
	bool __atomic_compare_exchange_4(volatile void* atomic_value, void* expected_value, unsigned int new_value, bool weak, int success_model, int failure_model) noexcept;
}
