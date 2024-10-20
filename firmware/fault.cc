/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>
#include <atomic>
#include <array>

#include "fault.hh"

std::atomic<fault_code_t> active_fault{fault_code_t::None};
