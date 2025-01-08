/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_PLATFORM_HH)
#define SQUISHY_SUPERVISOR_PLATFORM_HH

void start() noexcept;
void irq_eic() noexcept;

#endif /* SQUISHY_SUPERVISOR_PLATFORM_HH */
