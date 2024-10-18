/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstddef>
#include <cstdint>

extern "C" {
	[[gnu::optimize("-fno-tree-loop-distribute-patterns")]]
	void* memcpy(void* dest, const void* src, const std::size_t size) noexcept {
		auto* dest_buff{reinterpret_cast<std::uint8_t*>(dest)};
		const auto* src_buff{reinterpret_cast<const std::uint8_t*>(src)};

		for(std::size_t idx{}; idx < size; ++idx) {
			dest_buff[idx] = src_buff[idx];
		}

		return dest;
	}

	[[gnu::optimize("-fno-tree-loop-distribute-patterns")]]
	void* memset(void* dest, const std::uint8_t val, const std::size_t size) noexcept {
		auto* dest_buff{reinterpret_cast<std::uint8_t*>(dest)};

		for(std::size_t idx{}; idx < size; ++idx) {
			dest_buff[idx] = val;
		}

		return dest;
	}

	[[gnu::optimize("-fno-tree-loop-distribute-patterns")]]
	std::int32_t memcmp(const void* lhs, const void* rhs, const std::size_t size) noexcept {
		const auto* lhs_buff{reinterpret_cast<const std::uint8_t*>(lhs)};
		const auto* rhs_buff{reinterpret_cast<const std::uint8_t*>(rhs)};

		for(std::size_t idx{}; idx < size; ++idx) {
			if (lhs_buff[idx] > rhs_buff[idx]) {
				return 1;
			} else if (lhs_buff[idx] < rhs_buff[idx]) {
				return -1;
			}
		}

		return 0;
	}

}
