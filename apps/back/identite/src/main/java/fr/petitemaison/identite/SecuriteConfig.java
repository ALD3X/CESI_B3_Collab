package fr.petitemaison.identite;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecuriteConfig {

    @Bean
    SecurityFilterChain filtres(HttpSecurity http) throws Exception {
        return http
                // API sans session ni cookie : pas de jeton CSRF nécessaire
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(r -> r
                        .requestMatchers("/api/identite/connexion", "/actuator/health/**").permitAll()
                        .anyRequest().denyAll())
                .build();
    }
}
